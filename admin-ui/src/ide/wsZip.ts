/**
 * ZIP writer/reader for the /ide workspace export/import data layer.
 *
 * Pure data + Uint8Array module: no DOM, no browser-only APIs.
 * Uses the STORE method (compression=0) so output is deterministic
 * and dependency-free. File names are UTF-8 encoded with the EFS
 * flag (general purpose bit 11) set.
 */

/** Language value used for Python files in the /ide workspace records. */
export type WorkspaceLanguage = 'python' | 'markdown' | 'plaintext';

/** A workspace file record as stored in IndexedDB. */
export interface WorkspaceFile {
	name: string;
	language: string;
	content: string;
}

/** Parsed workspace file record returned by the ZIP reader. */
export interface ParsedWorkspaceFile {
	name: string;
	language: string;
	content: string;
}

/* ------------------------------------------------------------------ */
/* CRC-32 (IEEE 802.3)                                                 */
/* ------------------------------------------------------------------ */

const CRC_TABLE = (() => {
	const table = new Uint32Array(256);
	for (let n = 0; n < 256; n++) {
		let c = n;
		for (let k = 0; k < 8; k++) {
			c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
		}
		table[n] = c >>> 0;
	}
	return table;
})();

/**
 * Standard CRC-32 (IEEE) checksum of a byte array.
 *
 * @param data bytes to checksum
 * @returns unsigned 32-bit CRC
 */
export function crc32(data: Uint8Array): number {
	let crc = 0xffffffff;
	for (let i = 0; i < data.length; i++) {
		crc = CRC_TABLE[(crc ^ data[i]) & 0xff] ^ (crc >>> 8);
	}
	return (crc ^ 0xffffffff) >>> 0;
}

/* ------------------------------------------------------------------ */
/* Byte helpers                                                        */
/* ------------------------------------------------------------------ */

const encoder = new TextEncoder();
const decoder = new TextDecoder();

/** Encode a JS string to UTF-8 bytes. */
function textToU8(text: string): Uint8Array {
	return encoder.encode(text);
}

/** Decode UTF-8 bytes to a JS string. */
function u8ToText(bytes: Uint8Array): string {
	return decoder.decode(bytes);
}

/** Append little-endian 16-bit value into a buffer. */
function writeU16(target: Uint8Array, offset: number, value: number): void {
	target[offset] = value & 0xff;
	target[offset + 1] = (value >>> 8) & 0xff;
}

/** Append little-endian 32-bit value into a buffer. */
function writeU32(target: Uint8Array, offset: number, value: number): void {
	target[offset] = value & 0xff;
	target[offset + 1] = (value >>> 8) & 0xff;
	target[offset + 2] = (value >>> 16) & 0xff;
	target[offset + 3] = (value >>> 24) & 0xff;
}

/** Read a little-endian 16-bit value from a buffer. */
function readU16(source: Uint8Array, offset: number): number {
	return (source[offset] | (source[offset + 1] << 8)) >>> 0;
}

/** Read a little-endian 32-bit value from a buffer. */
function readU32(source: Uint8Array, offset: number): number {
	return (
		(source[offset] |
			(source[offset + 1] << 8) |
			(source[offset + 2] << 16) |
			(source[offset + 3] << 24)) >>>
		0
	);
}

/** Concatenate byte arrays into one. */
function concatBytes(parts: Uint8Array[]): Uint8Array {
	let total = 0;
	for (const part of parts) total += part.length;
	const out = new Uint8Array(total);
	let offset = 0;
	for (const part of parts) {
		out.set(part, offset);
		offset += part.length;
	}
	return out;
}

/* ------------------------------------------------------------------ */
/* ZIP constants                                                       */
/* ------------------------------------------------------------------ */

const LOCAL_HEADER_MAGIC = 0x04034b50; // PK\x03\x04
const CENTRAL_HEADER_MAGIC = 0x02014b50; // PK\x01\x02
const EOCD_MAGIC = 0x06054b50; // PK\x05\x06

const VERSION_NEEDED = 20;
const GPBF_EFS = 0x0800; // bit 11: UTF-8 encoded names
const METHOD_STORE = 0;

/** Fixed DOS date/time stamp: 2026-01-01 00:00:00 (deterministic output). */
const DOS_TIME = 0;
const DOS_DATE = ((2026 - 1980) << 9) | (1 << 5) | 1;

/* ------------------------------------------------------------------ */
/* Writer                                                              */
/* ------------------------------------------------------------------ */

interface PreparedEntry {
	nameBytes: Uint8Array;
	dataBytes: Uint8Array;
	crc: number;
}

/**
 * Build a valid ZIP archive (local headers + central directory + EOCD)
 * with each file stored uncompressed (STORE method). Names are UTF-8
 * with the EFS flag set, so spaces/Cyrillic survive round-trips.
 *
 * @param files workspace file records
 * @returns the ZIP archive bytes
 */
export function buildWorkspaceZip(files: WorkspaceFile[]): Uint8Array {
	const prepared: PreparedEntry[] = files.map((file) => {
		const nameBytes = textToU8(file.name);
		const dataBytes = textToU8(file.content);
		return {
			nameBytes,
			dataBytes,
			crc: crc32(dataBytes),
		};
	});

	const parts: Uint8Array[] = [];
	const centralRecords: Uint8Array[] = [];
	let offset = 0;

	for (const entry of prepared) {
		const local = new Uint8Array(30 + entry.nameBytes.length);
		writeU32(local, 0, LOCAL_HEADER_MAGIC);
		writeU16(local, 4, VERSION_NEEDED);
		writeU16(local, 6, GPBF_EFS);
		writeU16(local, 8, METHOD_STORE);
		writeU16(local, 10, DOS_TIME);
		writeU16(local, 12, DOS_DATE);
		writeU32(local, 14, entry.crc);
		writeU32(local, 18, entry.dataBytes.length); // compressed = size for STORE
		writeU32(local, 22, entry.dataBytes.length); // uncompressed size
		writeU16(local, 26, entry.nameBytes.length);
		writeU16(local, 28, 0); // extra field length
		local.set(entry.nameBytes, 30);
		parts.push(local, entry.dataBytes);

		const central = new Uint8Array(46 + entry.nameBytes.length);
		writeU32(central, 0, CENTRAL_HEADER_MAGIC);
		writeU16(central, 4, VERSION_NEEDED); // version made by
		writeU16(central, 6, VERSION_NEEDED); // version needed
		writeU16(central, 8, GPBF_EFS);
		writeU16(central, 10, METHOD_STORE);
		writeU16(central, 12, DOS_TIME);
		writeU16(central, 14, DOS_DATE);
		writeU32(central, 16, entry.crc);
		writeU32(central, 20, entry.dataBytes.length);
		writeU32(central, 24, entry.dataBytes.length);
		writeU16(central, 28, entry.nameBytes.length);
		// 30..41: extra/comment lengths, disk numbers, internal/external attrs = 0
		writeU32(central, 42, offset); // local header offset
		central.set(entry.nameBytes, 46);
		centralRecords.push(central);

		offset += local.length + entry.dataBytes.length;
	}

	const centralDirectory = concatBytes(centralRecords);
	parts.push(centralDirectory);

	const eocd = new Uint8Array(22);
	writeU32(eocd, 0, EOCD_MAGIC);
	// 4..7: disk numbers = 0
	writeU16(eocd, 8, prepared.length);
	writeU16(eocd, 10, prepared.length);
	writeU32(eocd, 12, centralDirectory.length);
	writeU32(eocd, 16, offset); // central directory offset
	// 20..21: comment length = 0
	parts.push(eocd);

	return concatBytes(parts);
}

/* ------------------------------------------------------------------ */
/* Reader                                                              */
/* ------------------------------------------------------------------ */

/**
 * Map a file name to its workspace language.
 *
 * @param name file name
 * @returns 'python' for .py, 'markdown' for .md (case-insensitive), else 'plaintext'
 */
export function languageForName(name: string): string {
	const lower = name.toLowerCase();
	if (lower.endsWith('.py')) return 'python';
	if (lower.endsWith('.md')) return 'markdown';
	return 'plaintext';
}

/**
 * Locate the End Of Central Directory record by scanning the tail of
 * the archive for the PK\x05\x06 magic.
 */
function findEocd(bytes: Uint8Array): number {
	const minEocd = 22;
	const maxComment = 0xffff;
	const from = Math.max(0, bytes.length - minEocd - maxComment);
	for (let i = bytes.length - minEocd; i >= from; i--) {
		if (readU32(bytes, i) === EOCD_MAGIC) return i;
	}
	throw new Error('Не zip-архив');
}

/**
 * Read a ZIP archive produced by buildWorkspaceZip back into workspace
 * file records. Directory entries (names ending in '/') are skipped.
 *
 * @param bytes ZIP archive bytes
 * @returns parsed workspace file records with derived languages
 */
export function parseWorkspaceZip(bytes: Uint8Array): ParsedWorkspaceFile[] {
	const eocdOffset = findEocd(bytes);
	const entryCount = readU16(bytes, eocdOffset + 10);
	const centralOffset = readU32(bytes, eocdOffset + 16);

	const files: ParsedWorkspaceFile[] = [];
	let cursor = centralOffset;

	for (let i = 0; i < entryCount; i++) {
		if (readU32(bytes, cursor) !== CENTRAL_HEADER_MAGIC) {
			throw new Error('Не zip-архив');
		}
		const method = readU16(bytes, cursor + 10);
		const crc = readU32(bytes, cursor + 16);
		const compressedSize = readU32(bytes, cursor + 20);
		const uncompressedSize = readU32(bytes, cursor + 24);
		const nameLength = readU16(bytes, cursor + 28);
		const extraLength = readU16(bytes, cursor + 30);
		const commentLength = readU16(bytes, cursor + 32);
		const localOffset = readU32(bytes, cursor + 42);
		const name = u8ToText(bytes.subarray(cursor + 46, cursor + 46 + nameLength));
		cursor += 46 + nameLength + extraLength + commentLength;

		// Directory marker entries (empty names ending with '/') are skipped.
		if (name.endsWith('/')) continue;
		if (method !== METHOD_STORE) {
			throw new Error('Архив сжат: повтори экспорт без сжатия');
		}

		if (readU32(bytes, localOffset) !== LOCAL_HEADER_MAGIC) {
			throw new Error('Не zip-архив');
		}
		const localNameLength = readU16(bytes, localOffset + 26);
		const localExtraLength = readU16(bytes, localOffset + 28);
		const dataStart = localOffset + 30 + localNameLength + localExtraLength;
		const dataBytes = bytes.subarray(dataStart, dataStart + compressedSize);

		if (dataBytes.length !== uncompressedSize || crc32(dataBytes) !== crc) {
			throw new Error('Не zip-архив');
		}

		files.push({
			name,
			language: languageForName(name),
			content: u8ToText(dataBytes),
		});
	}

	return files;
}
