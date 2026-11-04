class Playlist:
    def __init__(self, tracks):
        pass  # твой код: запомни tracks

    def __len__(self):
        pass  # твой код: верни число треков

    def __getitem__(self, index):
        pass  # твой код: верни трек по индексу, за границей IndexError("нет такого трека")


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
