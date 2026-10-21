def task_fn14_packs(items, per_pack):
    packs = items // per_pack
    if items % per_pack != 0:
        packs = packs + 1
    return packs
