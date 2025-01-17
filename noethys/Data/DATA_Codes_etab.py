#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-20 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import re


CODES_ETAB = """
001 AA 002 AB 003 AC 004 AD 005 AE 006 AF 007 AG 008 AH 009 AI 010 AJ
011 AK 012 AL 013 AM 014 AN 015 AO 016 AP 017 AQ 018 AR 019 AS 020 AT
021 AU 022 AV 023 AW 024 AX 025 AY 026 AZ 027 BA 028 BB 029 BC 030 BD
031 BE 032 BF 033 BG 034 BH 035 BI 036 BJ 037 BK 038 BL 039 BM 040 BN
041 BO 042 BP 043 BQ 044 BR 045 BS 046 BT 047 BU 048 BV 049 BW 050 BX
051 BY 052 BZ 053 CA 054 CB 055 CC 056 CD 057 CE 058 CF 059 CG 060 CH
061 CI 062 CJ 063 CK 064 CL 065 CM 066 CN 067 CO 068 CP 069 CQ 070 CR
071 CS 072 CT 073 CU 074 CV 075 CW 076 CX 077 CY 078 CZ 079 DA 080 DB
081 DC 082 DD 083 DE 084 DF 085 DG 086 DH 087 DI 088 DJ 089 DK 090 DL
091 DM 092 DN 093 DO 094 DP 095 DQ 096 DR 097 DS 098 DT 099 DU 100 DV
101 DW 102 DX 103 DY 104 DZ 105 EA 106 EB 107 EC 108 ED 109 EE 110 EF
111 EG 112 EH 113 EI 114 EJ 115 EK 116 EL 117 EM 118 EN 119 EO 120 EP
121 EQ 122 ER 123 ES 124 ET 125 EU 126 EV 127 EW 128 EX 129 EY 130 EZ
131 FA 132 FB 133 FC 134 FD 135 FE 137 FG 138 FH 139 FI 140 FJ 141 FK
142 FL 143 FM 144 FN 145 FO 146 FP 147 FQ 148 FR 149 FS 150 FT 151 FU
152 FV 153 FW 154 FX 155 FY 156 FZ 157 GA 158 GB 159 GC 160 GD 161 GE
162 GF 163 GG 164 GH 165 GI 166 GJ 167 GK 168 GL 169 GM 170 GN 171 GO
172 GP 173 GQ 174 GR 175 GS 176 GT 177 GU 178 GV 179 GW 180 GX 181 GY
182 GZ 183 HA 184 HB 185 HC 186 HD 187 HE 188 HF 189 HG 190 HH 191 HI
192 HJ 193 HK 194 HL 195 HM 196 HN 197 HO 198 HP 199 HQ 200 HR 201 HS
202 HT 203 HU 204 HV 205 HW 206 HX 207 HY 208 HZ 209 IA 210 IB 211 IC
212 ID 213 IE 214 IF 215 IG 216 IH 217 II 218 IJ 219 IK 220 IL 221 IM
222 IN 223 IO 224 IP 225 IQ 226 IR 227 IS 228 IT 229 IU 230 IV 231 IW
232 IX 233 IY 234 IZ 235 JA 236 JB 237 JC 238 JD 239 JE 240 JF 241 JG
242 JH 243 JI 244 JJ 245 JK 246 JL 247 JM 248 JN 249 JO 250 JP 251 JQ
252 JR 253 JS 254 JT 255 JU 256 JV 257 JW 258 JX 259 JY 260 JZ 261 KA
262 KB 263 KC 264 KD 265 KE 266 KF 267 KG 268 KH 269 KI 270 KJ 271 KK
272 KL 273 KM 274 KN 275 KO 276 KP 277 KQ 278 KR 279 KS 280 KT 281 KU
282 KV 283 KW 284 KX 285 KY 286 KZ 287 LA 288 LB 289 LC 290 LD 291 LE
292 LF 293 LG 294 LH 295 LI 296 LJ 297 LK 298 LL 299 LM 300 LN 301 LO
302 LP 303 LQ 304 LR 305 LS 306 LT 307 LU 308 LV 309 LW 310 LX 311 LY
312 LZ 313 MA 314 MB 315 MC 316 MD 317 ME 318 MF 319 MG 320 MH 321 MI
322 MJ 323 MK 324 ML 325 MM 326 MN 327 MO 328 MP 329 MQ 330 MR 331 MS
332 MT 333 MU 334 MV 335 MW 336 MX 337 MY 338 MZ 339 NA 340 NB 341 NC
342 ND 343 NE 344 NF 345 NG 346 NH 347 NI 348 NJ 349 NK 350 NL 351 NM
352 NN 353 NO 354 NP 355 NQ 356 NR 357 NS 358 NT 359 NU 360 NV 361 NW
362 NX 363 NY 364 NZ 365 OA 366 OB 367 OC 368 OD 369 OE 370 OF 371 OG
372 OH 373 OI 374 OJ 375 OK 376 OL 377 OM 378 ON 379 OO 380 OP 381 OQ
382 OR 383 OS 384 OT 385 OU 386 OV 387 OW 388 OX 389 OY 390 OZ 391 PA
392 PB 393 PC 394 PD 395 PE 396 PF 397 PG 398 PH 399 PI 400 PJ 401 PK
402 PL 403 PM 404 PN 405 PO 406 PP 407 PQ 408 PR 409 PS 410 PT 411 PU
412 PV 413 PW 414 PX 415 PY 416 PZ 417 QA 418 QB 419 QC 420 QD 421 QE
422 QF 423 QG 424 QH 425 QI 426 QJ 427 QK 428 QL 429 QM 430 QN 431 QO
432 QP 433 QQ 434 QR 435 QS 436 QT 437 QU 438 QV 439 QW 440 QX 441 QY
442 QZ 443 RA 444 RB 445 RC 446 RD 447 RE 448 RF 449 RG 450 RH 451 RI
452 RJ 453 RK 454 RL 455 RM 456 RN 457 RO 458 RP 459 RQ 460 RR 461 RS
462 RT 463 RU 464 RV 465 RW 466 RX 467 RY 468 RZ 469 SA 470 SB 471 SC
472 SD 473 SE 474 SF 475 SG 476 SH 477 SI 478 SJ 479 SK 480 SL 481 SM
482 SN 483 SO 484 SP 485 SQ 486 SR 487 SS 488 ST 489 SU 490 SV 491 SW
492 SX 493 SY 494 SZ 495 TA 496 TB 497 TC 498 TD 499 TE 500 TF 501 TG
502 TH 503 TI 504 TJ 505 TK 506 TL 507 TM 508 TN 509 TO 510 TP 511 TQ
512 TR 513 TS 514 TT 515 TU 516 TV 517 TW 518 TX 519 TY 520 TZ 521 UA
522 UB 523 UC 524 UD 525 UE 526 UF 527 UG 528 UH 529 UI 530 UJ 531 UK
532 UL 533 UM 534 UN 535 UO 536 UP 537 UQ 538 UR 539 US 540 UT 541 UU
542 UV 543 UW 544 UX 545 UY 546 UZ 547 VA 548 VB 549 VC 550 VD 551 VE
552 VF 553 VG 554 VH 555 VI 556 VJ 557 VK 558 VL 559 VM 560 VN 561 VO
562 VP 563 VQ 564 VR 565 VS 566 VT 567 VU 568 VV 569 VW 570 VX 571 VY
572 VZ 573 WA 574 WB 575 WC 576 WD 577 WE 578 WF 579 WG 580 WH 581 WI
582 WJ 583 WK 584 WL 585 WM 586 WN 587 WO 588 WP 589 WQ 590 WR 591 WS
592 WT 593 WU 594 WV 595 WW 596 WX 597 WY 598 WZ 599 XA 600 XB 601 XC
602 XD 603 XE 604 XF 605 XG 606 XH 607 XI 608 XJ 609 XK 610 XL 611 XM
612 XN 613 XO 614 XP 615 XQ 616 XR 617 XS 618 XT 619 XU 620 XV 621 XW
622 XX 623 XY 624 XZ 625 YA 626 YB 627 YC 628 YD 629 YE 630 YF 631 YG
632 YH 633 YI 634 YJ 635 YK 636 YL 637 YM 638 YN 639 YO 640 YP 641 YQ
642 YR 643 YS 644 YT 645 YU 646 YV 647 YW 648 YX 649 YY 650 YZ 651 ZA
652 ZB 653 ZC 654 ZD 655 ZE 656 ZF 657 ZG 658 ZH 659 ZI 660 ZJ 661 ZK
662 ZL 663 ZM 664 ZN 665 ZO 666 ZP 667 ZQ 668 ZR 669 ZS 670 ZT 671 ZU
672 ZV 673 ZW 674 ZX 675 ZY 676 ZZ
"""


def Rechercher(code=""):
    regex = re.compile(r"([0-9][0-9][0-9]) ([A-Z][A-Z])")
    dict_codes = {}
    for numerique, lettres in regex.findall(CODES_ETAB):
        dict_codes[lettres] = numerique
    return dict_codes.get(code, code)


if __name__ == "__main__":
    print(Rechercher("RS"))


