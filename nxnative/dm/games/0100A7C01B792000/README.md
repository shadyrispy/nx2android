# Minecraft Dungeons II (`0100A7C01B792000`)

Update 1.1.3.0 (v131072) over the base game v65536, SDK 20.5.15. Mojang's Unreal Engine 5 game on the engine's desktop renderer (`SF_GLSL_SWITCH` shaders, not the mobile one), NVN, Wwise sound, Havok, Xbox network services (offline here), H.264 / AAC logo movies through the SDK's movie library. Modules `main`, `subsdk0` (the movie library) and `sdk`. The base game is sparse: its Program and one HtmlDocument NCA leave out data its update carries, so only the update is packed ([Sparse base games](../../../docs/reference/packing.md#sparse-base-games)).

Status: on the Mac (2026-11-06, M4 Pro), from a fresh save: the Xbox Game Studios logo movie, the title, the first-run accessibility, brightness and terms screens, the online / offline choice (online is unavailable, as the host is offline; Play Offline), the main menu, Entering World, the in-engine opening cutscene (skipped with B) and first control in Escape from Squid Coast, walking and attacking. 30 fps (the game's own rate) at 1920x1080 with no `[RED]` line, about 2.6 GB resident at frame 4,200. 60 fps, and up to 120 on the Mac, since 2026-11-08. The IPA is not built. On the iPad mini (A17 Pro, 2026-11-12), from the XCI's own version (v65536, 1.1.1, a derived profile) and the iPhone block below: it boots, plays its audio and presents 289 of 300 frames with no `[RED]` line at 1,292 MiB; the Mac build of that version, with `DM_ALIAS_SIZE=0x118000000`, gives the same engine region, 4.06 GB.

## What it needs

| Setting | Where | Why |
|---|---|---|
| `tex_dyn_slots on` | [`game.tsv`](game.tsv) | 2 particle vertex shaders pick a buffer texture at run time; see [Shaders](#shaders) |
| `mem_reserve 0x140000000`, `mem_alias 0x118000000`, `mem_stack 0x10000000`, `app_pool 0xCD500000` | [`game.tsv`](game.tsv) | the iPhone block of the same engine version ([FINAL FANTASY RESONANCE](../0100606026F12000/README.md#memory), engine region 4.06 GB): the rewriter's engine-wide rules cut FMallocBinned3's constructor (`dm/tools/ue_malloc.py`) and give the engine region what the alias region has room for (`dm/tools/ue_region.py`). iOS allows one reservation of at most 6 GB, so the 64 GB block from the Mac bring-up aborts at `nnosInitialize` there; on the Mac the host reserves the larger of this and the Switch's 64 GB |
| `sys_resource 0x1400000` | `game.tsv` | the NPDM declares 20 MB of system resource |
| `shader_groups ShaderArchive-Global-=global ShaderArchive-=game`, `depth_mode zero` | `game.tsv` | the two shader code archives; the game sets near = 0 depth |

No host or rewriter rule is specific to this game.

## Frame rate

- **Resolved: the game stopped presenting right after the logo movie** (game thread in `FlushRenderingCommands`, `main+0x14fd670`, waking each millisecond in `FFrameEndSync::Sync`, `main+0x15015f0`; render, RHI, frame-flip and interrupt threads idle). The RHI's "Viewport Thread" (`main+0x142afb0`) learns of each flip from `nn::vi::ListFrameHistory` after each vsync (`main+0x142b034`, `+0x142b094`), and the host answered with no entries, so the swap-chain fences never completed: [Layer frame history](../../../docs/reference/services.md#layer-frame-history). Found by the thread dumps at one-second steps (`DM_CTL` `dump`), the event's never-set trigger word, and reading the waiting functions (no symbols; this part of `main` has no unwind entries).
- **Current: 60 fps, up to 120 on the Mac** (`fps_target 60`, `fps_max 120`). The game's config sets `rhi.SyncInterval` 2 and `t.MaxFPS` 0 (no limit), and its `bUseFixedFrameRate` is off, so its engine steps by the time that really passed and the present interval the host writes is all it needs ([Unreal's frame limit and present interval, found by name](../../../docs/reference/frame-rate.md#unreals-frame-limit-and-present-interval-found-by-name); `rhi.SyncInterval` at `main+0xac96a10`). Measured on an M4 Pro (2026-11-08, chain `89f44f9b6bb0`, headless, a copy of the same save past the first-run screens, title → Play → cutscene skipped → right 2 s, down 1.5 s): frame time p50 33.4 ms at 30, 16.7 at 60, 8.3 at 120 (118.5 fps), no `[RED]` line, and the walk ends at the same spot at all three. At 120 the title and loads drop to 60 for a moment (a logo movie holds 60). The user played Squid Coast at 120 in a window and judged the speed right.
- **Open:** the engine's `UEngine::FixedFrameRate` reflection entry has a layout `dm/tools/ue_fixed_rate.py` does not read (the setter and getter at +32 / +40, a 16-bit array size at +48, the offset at +52: `+0xc38`, its flag bit 0x40 of `+0xc34`, `GEngine` at `main+0xae26e30`), so it finds no fixed frame rate here. It makes no difference to this game, whose flag is off; a game on this engine version with the flag on would stay at its fixed rate.

## Shaders

- 16,751 shaders in two shader code archives of the IoStore containers (`ShaderArchive-Dungeons-SF_GLSL_SWITCH-SP_GLSL_SWITCH.ushaderbytecode` 13,318, `ShaderArchive-Global-…` 3,433), decoded by the NSP script; 15,826 unique after the split, all translated for the Mac. The translator deletes one bindless access in `ccd515f16b0f63a6` (a `texture2DArray`, which reads 0); no run has used that shader.
- **Resolved: the title's campfire flame was black** (`[RED] shader 210d8abb3b9996c5_b reflection conversion failed: a texture handle the translator could not trace to one slot`, the same for `d1c8e612ec7462b6`). The two particle vertex shaders read a buffer texture whose handle they pick at run time: a c2 texture-table word ORed with a sampler-table word. Their only c2 reads are texture table words 0x170-0x188 and sampler table words 0x568 / 0x578, so `tex_dyn_slots on` is right here, as for Octopath Traveler 0's and FINAL FANTASY RESONANCE's.

## On the Mac

- After the NSP script's `--platform mac` build, its printed command runs the game; with `DM_FOCUS_KEEP=1 DM_WINDOW_TOP=1` a host started from a background shell keeps presenting.
- From a fresh save: A at the title, X on the accessibility and brightness screens, X to agree to the terms, Right and A for Play Offline, A on Play, then B held to skip the opening cutscene.

## Found on this game

- [Unreal's frame limit and present interval, found by name](../../../docs/reference/frame-rate.md#unreals-frame-limit-and-present-interval-found-by-name): 60 and 120 by `rhi.SyncInterval` alone
- [Layer frame history](../../../docs/reference/services.md#layer-frame-history)
- [The offline pages of a sparse base game stop the build as a damaged NSP](../../../docs/reference/packing.md#the-offline-pages-of-a-sparse-base-game-stop-the-build-as-a-damaged-nsp)
- [The survey's build ID lookup stops on the base game alone with a hash error](../../../docs/reference/packing.md#the-surveys-build-id-lookup-stops-on-the-base-game-alone-with-a-hash-error)
- [A shader build leaves a file per shader output while it runs or after a stop](../../../docs/reference/packing.md#a-shader-build-leaves-a-file-per-shader-output-while-it-runs-or-after-a-stop): measured here, its 61,655 library files the same under the new chain
- [Writes beside a packaged texture in a shared host page](../../../docs/reference/nvn-objects.md#writes-beside-a-packaged-texture-in-a-shared-host-page): after GPU stores into packaged textures' storage, 17 small textures were uploaded again by writes beside them, until the stores wrote their edge bytes too

## Open

- The prewarm list (`pso_manifest.tsv`) is empty.
- Only the start of the first level was played: later levels, couch co-op (more controllers), saves across boots and the other languages are untested.

## Android

Brought up 2026-11-15 on a Redmi 2410DPN6CC (Snapdragon 8 Elite, Adreno 830, Android 16): the camp menu and the first level at 60 fps (frame time p50 16.56 ms, p95 17.84 ms), no [RED] line, audio without an underrun. Built from the iOS build's own extraction (the NAS XCI has since gone bad: sha256 equal on both sides, LibHac `PartitionSignatureVerificationFailed`), with the shader archives decoded offline by ooz (`lvlvllvlvllvlvl/oozextract`) instead of the game's decoder, and `ue_shaders` reused from the iOS extraction (its stamp matches the seeded RomFS).

What the port needed (all in this branch's host and this profile's `patches.py`):

- **The engine region is cut to 4 GB** (`patches.py`, `0x14380`: the 62 GB default → 0x100000000) and **FMallocBinned3's constructor is cut** (`0x143b0` → nop), with the object's vtable from `hle_uemalloc.c` (bss object 0x9979228, vtable 0x85b68a8, UE 5.6 layout): 62 GB + the allocator's 37 GB does not fit a Switch's 64 GB alias, and the allocator crashed at main+0x141619c without the cut.
- **The alias region is the Switch's 64 GB** when the profile says less (`hle_svc.c`, as upstream): the 4 GB region then has room.
- **`vi::ListFrameHistory` returns the last 8 presents** (`hle_vi.c`, fed by `hle_nvn.c`): with 0 entries the game's frame fence never completed and the boot stopped for good after the intro (`GameThread timed out waiting for RenderThread`).
- **`ssl::Context::Create/Destroy` succeed offline** (`hle_net.c`), with the offline module's entries from upstream merged in (`hle_offline.c`): XblInitialize then fails harmlessly at boot instead of aborting; the game offers Play Offline.
- **`t.MaxFPS` and `rhi.SyncInterval` are raised** (`hle_fpslock.c`, the same addresses the iOS fixups name): the Switch device profile asks 30 fps at vsync interval 2; the profile's `fps_target 60` takes it to 60 fps.
- **The rewriter's online/offline takeover list tolerates a duplicate** (`loader.c`): the fork's own ldn/socket modules and the merged offline entries overlap, which used to be fatal at start.
- `nn::account::AsyncContext`'s constructor is no longer taken over (`hle_account.c`, as upstream): a no-op left the object's vtable and IPC pointer unset.
- NX2Android's `RomFS` folder must be readable by the app (`chmod -R a+rX` after a push: 2770 with the shell owner gave errno 13 and `PreInit() failed`).

Open here:

- **Water and tunnels render pure black.** Not investigated yet (the pool/tunnel geometry draws, its surface is black).
- **A cutscene starts with a ~3.5 s frame** (log: `frame time ... max 3511.14 ms`): `movie_avc.c` opens the hardware decoder when the movie starts and destroys it after; the decoder should be kept/warmed.
- 120 fps (the iPhone profile's `fps_max`) is not tried: the host's fps target accepts 30 and 60, and the Android surface is created at 60 Hz.
