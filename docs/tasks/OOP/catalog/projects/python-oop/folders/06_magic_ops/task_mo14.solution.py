class Playlist:
    def __init__(self, tracks):
        self.tracks = tracks

    def __len__(self):
        return len(self.tracks)

    def __getitem__(self, index):
        if not -len(self.tracks) <= index < len(self.tracks):
            raise IndexError("нет такого трека")
        return self.tracks[index]


# ===== Ниже ничего не меняй: это рамка для проверки. =====

def task_mo14_playlist(tracks, indexes):
    playlist = Playlist(tracks)
    results = []
    for index in indexes:
        try:
            results.append(playlist[index])
        except IndexError as error:
            results.append(["IndexError", str(error)])
    return {"len": len(playlist), "items": results}
