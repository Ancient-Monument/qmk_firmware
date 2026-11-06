# AM34

A handwired test build of the [AM37](../am37/readme.md) layout: 34 keys, Gateron KS-33 low-profile switches and a Keebio Elite-Pi, made to try two Cirque trackpads and a small display before changing any PCB. Its parts, wiring and build guide are in [Ancient-Monument/keyboards](https://github.com/Ancient-Monument/keyboards/tree/main/am34).

This firmware covers the key matrix only. The trackpads and display have no firmware yet.

* The matrix is the AM37's, 4 rows by 10 columns, COL2ROW, on new pins. Rows are on `F4 F6 F5 F7` and columns on `B1 B3 B2 B6 B5 E6 D0 D1 D2 D3`, as Elite-C pin names; `rules.mk` converts them for the Elite-Pi.
* The keymap is the AM37's without its underglow, since the AM34 has no LEDs. The AM34 does not have the AM37's three centre thumb keys, so the keycodes on them cannot be reached: Mic Toggle, Screen Lock and Zoom End on the base layer, Cam Toggle on the symbol layer, and Reset (`QK_BOOT`) on the arrows and symbol layers. Bootmagic takes Reset's place: hold Q while plugging the AM34 in to start the Elite-Pi's bootloader.

* **Keyboard Maintainer**: Ross Harmes
* **Hardware Availability**: handwired; see the build guide linked above.

Build it with:

    qmk compile -kb handwired/am34 -km default

That writes `handwired_am34_default.uf2`. Hold Q while plugging the AM34 in, or double-tap the Elite-Pi's reset button, to start its bootloader, and copy the file to the `RPI-RP2` drive it shows.
