# Minecraft Dungeons II (0100A7C01B792000) 1.1.1 main (build 9e9d887d…): the rewriter's patches of this build. UE5's nninitStartup reserves a 62 GB engine address region and
# FMallocBinned3's constructor takes 37 GB of pools inside it (hle_uemalloc.c: on iOS neither fits, so both are cut and the host's allocator takes the vtable's place).
CUTS = {
  '9e9d887d59f7f7db176b35e3379258b9': [
    (0x14380, 'e81361b2', '2800c0d2', "nninitStartup: mov x8, #0xf80000000 (the 62 GB engine region default) → #0x100000000 (4 GB, what the iPhone build gets from the alias region; 62 GB plus the allocator's 37 GB does not fit a Switch's 64 GB alias)"),
    (0x143b0, '6c700294', '1f2003d5', "nninitStartup: bl 0xb0560 (FMallocBinned3 constructor, 37 GB of address space) → nop; the host allocator's vtable is put into the object at 0x9979228 (hle_uemalloc.c)"),
  ],
}
