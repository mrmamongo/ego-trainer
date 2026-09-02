import type { EgoConfigFile, EgoMode } from './egoWorkspace';

export interface SessionDecision {
    mode: EgoMode;
    apiToken: string | undefined;
    validateToken: boolean;
    offline: boolean;
    loggedIn: boolean;
    ready: boolean;
    status: EgoMode;
}

/** Decide runtime auth from workspace config; config mode is authoritative. */
export function decideSession(
    config: EgoConfigFile | undefined,
    storedToken: string | undefined
): SessionDecision {
    const mode: EgoMode = config?.mode === 'offline' ? 'offline' : 'server';
    const server = mode === 'server';
    return {
        mode,
        apiToken: server ? storedToken : undefined,
        validateToken: server && !!storedToken,
        offline: !server,
        loggedIn: false,
        ready: !!config,
        status: mode,
    };
}

/** Merge a new initialization config without discarding existing config fields. */
export function mergeEgoConfig(
    existing: Partial<EgoConfigFile> | undefined,
    supplied: EgoConfigFile
): EgoConfigFile {
    return { ...existing, ...supplied } as EgoConfigFile;
}

export interface EgoSkeletonPlan {
    config: EgoConfigFile;
    writeManifest: boolean;
    writeProgress: boolean;
}

/** Pure plan for idempotent initialization and preservation of user data. */
export function planEgoSkeleton(
    existing: Partial<EgoConfigFile> | undefined,
    supplied: EgoConfigFile,
    files: { manifest: boolean; progress: boolean }
): EgoSkeletonPlan {
    return {
        config: mergeEgoConfig(existing, supplied),
        writeManifest: !files.manifest,
        writeProgress: !files.progress,
    };
}
