# MM Calendar - אינוונטר ארטים מוכנים (Shiny Show In-App)

> נסרק אוטומטית מ-CRM3: `The_Shiny_Show/{2025,2026,Joker Promotions}`.
> מקור: `scripts/scan_shiny_art.py` (ניתן להרצה חוזרת). ספירה ברמת תיקיית-פרומו (כל תיקיה = פרומו עם Inapp art מוכן).

## סיכום

- סך פרומואים עם Inapp art מוכן: **144**
- **Generic** (מכניקה, ניתן לשימוש חוזר בכל זמן): **115**
- **Themed** (קשור לאירוע/חג/מותג): **29**

### פירוק themed לפי תמה

| תמה | פרומואים מוכנים |
|---|---|
| New Year | 4 |
| Valentine's Day | 3 |
| Christmas | 3 |
| Thanksgiving | 3 |
| Spring | 3 |
| Betty Boop (branded) | 2 |
| 4th of July | 2 |
| Super Bowl | 1 |
| Summer | 1 |
| Halloween | 1 |
| Black Friday | 1 |
| Birthday | 1 |
| St. Patrick's | 1 |
| Cinco de Mayo | 1 |
| World Cup | 1 |
| Lucy's Carnivale | 1 |

## איך האייג'נט משתמש בזה

- כשמשבצים Shiny Show ביום ללא אירוע -> להעדיף ארט **Generic** מוכן (reuse, ללא עלות ארט).
- כשיש אירוע/חג -> לבדוק אם יש ארט **Themed** מוכן לאותה תמה לפני הזמנת ארט חדש.
- שמות התיקיות מקודדים `YYYY_MM_DD_<תיאור>` - התאריך = מתי שומש לאחרונה.

### דוגמה מאומתת (Themed מול Generic - אותה מכניקה)
שני הארטים הבאים הם אותו פרומו ("Reach Act 21 to win a Wild Guaranteed") - אחד themed ואחד generic:
- **Themed**: `2026/2026_05_05_CincoDeMayo/SS_Wilds_Cards_Cinco_De_Mayo_Inapp.png` - מעוטר ב-papel picado + מרקס (Cinco de Mayo).
- **Generic**: `2026/2026_05_09_Shiny_Show_Wilds/inapp/SS_Shiny_Wilds_Inapp.png` - רקע תיאטרון ניטרלי, ללא קישוטי חג -> reusable.
מבנה תיקיית פרומו: `<promo>/*_Inapp.png` + תיקיות `Banner/`, `Intro/`, `PJMS/`, `Tooltip/` (גם `.psb` למקור).

## פרומואים Themed

| תיקיה (פרומו) | תמה | קבצי Inapp |
|---|---|---|
| 2025/2025_01_01_Shiny_Show_NY | New Year | 2 |
| 2025/2025_02_09_SS_Super_Bowl | Super Bowl | 4 |
| 2025/2025_02_14_SS_AF_Valentine_Day | Valentine's Day | 2 |
| 2025/2025_07_23_Shiny Show_Christmas_in_July | Christmas | 4 |
| 2025/2025_07_31_Shiny_Show_Summer Party | Summer | 4 |
| 2025/2025_10_31_Shiny_Show_Halloween | Halloween | 2 |
| 2025/2025_11_21_Shiny_Show_ThanksGiving | Thanksgiving | 2 |
| 2025/2025_11_24_Shiny_Show_Thanksgiving_Wild_Gold | Thanksgiving | 2 |
| 2025/2025_11_25_Shinyshow_Thanksgiving | Thanksgiving | 1 |
| 2025/2025_11_29_BF_Shiny_Show | Black Friday | 1 |
| 2025/2025_12_21_Crazy_with_Aces_xmas | Christmas | 6 |
| 2025/2025_12_25_Xmas_FindTrees | Christmas | 6 |
| 2026/2026_01_01_New_Year_SS_Chance_To_Win_Wild_Ordinary | New Year | 1 |
| 2026/2026_01_01_New_Year_SS_Crazy_With_Aces | New Year | 4 |
| 2026/2026_01_01_New_Year_SS_Different_Prizes | New Year | 1 |
| 2026/2026_01_29_SS_BDAY_Special_Aces | Birthday | 1 |
| 2026/2026_02_14_SS_All_Cards_Valentines | Valentine's Day | 1 |
| 2026/2026_02_14_Valentines_win_Aces | Valentine's Day | 1 |
| 2026/2026_02_16_SS_Find_Betty_to_win_a_Wild | Betty Boop (branded) | 2 |
| 2026/2026_03_06_SS_Find_Betty_Dash_Points | Betty Boop (branded) | 2 |
| 2026/2026_03_17_SS_St_Patricks_Crazy_mole | St. Patrick's | 6 |
| 2026/2026_04_13_SS_Different_Prizes_Spring | Spring | 1 |
| 2026/2026_04_15_Shiny_Show_24_Cards_Spring | Spring | 1 |
| 2026/2026_04_26_SS_Find_Bee_Win_Wilds_Spring_Theme | Spring | 1 |
| 2026/2026_05_05_CincoDeMayo | Cinco de Mayo | 1 |
| 2026/2026_06_13_SS_World_Cup_Special | World Cup | 1 |
| 2026/2026_07_04_Different_Prizes_4th_of_july | 4th of July | 1 |
| Joker Promotions/2026_05_22_SS_Lucy's_Carnivale_Day_01 | Lucy's Carnivale | 1 |
| Joker Promotions/2026_07_04_Different_Prizes_4th_of_july | 4th of July | 3 |

## פרומואים Generic

| תיקיה (פרומו) | תמה | קבצי Inapp |
|---|---|---|
| 2025/2025_ 12_04_All_Cards | - | 4 |
| 2025/2025_01_02_Shiny Show_All_cards​ | - | 1 |
| 2025/2025_01_06_SS_Fuse_All_Cards | - | 2 |
| 2025/2025_01_09_Crazy_SS_Aces | - | 8 |
| 2025/2025_01_10_SS_All_Cards_With_SB | - | 1 |
| 2025/2025_01_11_SS_5ACE_Pack | - | 1 |
| 2025/2025_01_14_SS_Carzy_Golds | - | 7 |
| 2025/2025_01_14_SS_Challenge | - | 5 |
| 2025/2025_01_16_SS_Gem_Jackpot | - | 10 |
| 2025/2025_01_20_SS_Dash_Points | - | 1 |
| 2025/2025_01_28_Shiny_Show_Party | - | 11 |
| 2025/2025_01_29_Crazy_Mole_Golds | - | 6 |
| 2025/2025_01_31_SS_Special_Acts | - | 1 |
| 2025/2025_02_03_SS_300_badges | - | 1 |
| 2025/2025_02_04_SS_All_Cards_Wild_Ace | - | 2 |
| 2025/2025_02_07_SS_Wild_Ordinary | - | 1 |
| 2025/2025_02_08_SS_Crazy_Aces_With_Wild | - | 12 |
| 2025/2025_02_11_SS_Fusion_Pieces | - | 2 |
| 2025/2025_02_12_SS_Fusion_Pieces | - | 1 |
| 2025/2025_02_15_SS_Wild_Any | - | 1 |
| 2025/2025_02_16_SS_Crazy_Fusion_Picecs | - | 3 |
| 2025/2025_02_17_SS_All_Cards | - | 1 |
| 2025/2025_02_19_SS_Special_Acts | - | 1 |
| 2025/2025_02_20_Shiny_Show_Wilds | - | 3 |
| 2025/2025_02_21_SS_All_Cards | - | 3 |
| 2025/2025_02_23_Shiny_show_fusion | - | 4 |
| 2025/2025_02_24_SS_Starter_Kit | - | 4 |
| 2025/2025_02_25_SS_All_Cards | - | 6 |
| 2025/2025_02_27_SS_Spacial_Acts | - | 2 |
| 2025/2025_03_10_SS_Wild_Fusion | - | 5 |
| 2025/2025_03_17_SS_Extra_Picks | - | 1 |
| 2025/2025_03_19_SS_SlotoCard_JP | - | 3 |
| 2025/2025_03_27_Spacial_Acts | - | 1 |
| 2025/2025_04_06_SS_Wild_Gold | - | 1 |
| 2025/2025_04_08_SS_BD_Wilds | - | 2 |
| 2025/2025_04_08_SS_Wild_Any | - | 2 |
| 2025/2025_04_10_SS_Special_Acts | - | 1 |
| 2025/2025_04_10_SS_Wheel_of_Fortune_IGT | - | 2 |
| 2025/2025_04_15_SS_Fusion_Pieces | - | 1 |
| 2025/2025_04_16_SS_Picks | - | 1 |
| 2025/2025_04_17_SS_Wild_Any | - | 1 |
| 2025/2025_04_19_SS_Special_Acts | - | 1 |
| 2025/2025_04_29_SS_Fusion_Pieces | - | 3 |
| 2025/2025_05_01_SS_Special_Act | - | 1 |
| 2025/2025_05_05_SS_Starter_Kit | - | 10 |
| 2025/2025_05_22_Shiny_Show_Dash | - | 3 |
| 2025/2025_05_27_SS_Album_Challenge | - | 4 |
| 2025/2025_05_28_Different_Acts | - | 1 |
| 2025/2025_06_05_Act_21_Gacha_prizes | - | 3 |
| 2025/2025_06_16_SS_SlotoCard_Wild_JP | - | 2 |
| 2025/2025_07_02_Spacial_Acts | - | 2 |
| 2025/2025_07_04_SS_SlotoCard_Wild_JP | - | 1 |
| 2025/2025_07_05_SS_All_Cards | - | 1 |
| 2025/2025_07_06_Crazy_wildWithGold | - | 1 |
| 2025/2025_07_10_SS_Fusion_Pieces | - | 1 |
| 2025/2025_07_18_Crazy_with_Aces | - | 4 |
| 2025/2025_07_18_Crazy_with_Aces - Copy | - | 4 |
| 2025/2025_07_18_SS_SlotoCard_JP | - | 1 |
| 2025/2025_07_28_Act_21_Gacha_prizes | - | 1 |
| 2025/2025_07_29_SS_SlotoCard_JP | - | 3 |
| 2025/2025_07_30_SS_Carzy_Golds | - | 5 |
| 2025/2025_08_07_Shiny_Show_Wilds | - | 2 |
| 2025/2025_08_14_Gacha_prizes_newCoin | - | 2 |
| 2025/2025_08_14_Gacha_prizes_newCoin_BD | - | 2 |
| 2025/2025_08_21_SS_Carzy_Golds_GoldenDay | - | 5 |
| 2025/2025_08_23_Shiny_Show_Wild_Ace_Coin_Value | - | 3 |
| 2025/2025_08_27_Shiny_Show_Limited | - | 3 |
| 2025/2025_09_01_SS_All_Cards | - | 1 |
| 2025/2025_09_03_Shiny_Show_Card_Jackpot | - | 1 |
| 2025/2025_09_11_SS_Fusion_Pieces | - | 1 |
| 2025/2025_09_14_Shiny_Show_Wild_Ordinary_NewCoin | - | 48 |
| 2025/2025_09_19_SS_All_Acts_Cards | - | 2 |
| 2025/2025_09_26_Shiny_Show_Special_Acts | - | 2 |
| 2025/2025_10_01_SS_All_Cards | - | 3 |
| 2025/2025_10_05_Shiny_Show | - | 1 |
| 2025/2025_10_27_Shiny_Show_Limited | - | 2 |
| 2025/2025_10_27_Shiny_Show_Limited - Copy | - | 2 |
| 2025/2025_10_28_Different_Acts | - | 2 |
| 2025/2025_11_01_Shiny_Show_Limited | - | 3 |
| 2025/2025_11_01_Shiny_Show_wild_Ace | - | 1 |
| 2025/2025_11_11_Veterans_Day | - | 1 |
| 2025/2025_11_14_Shiny_Show | - | 1 |
| 2025/2025_11_20_ShinyShow_AlbumTreatment | - | 2 |
| 2025/2025_12_02_SS#2 | - | 1 |
| 2025/2025_12_02_Shiny_Show | - | 1 |
| 2025/2025_12_06_Get_cards | - | 1 |
| 2025/2025_12_08_SS_Starter_Kit | - | 5 |
| 2025/2025_12_16_SS_3Stars_JP_Card | - | 1 |
| 2026/2025_01_06_SS_SlotoCard_JP_4_Cards | - | 1 |
| 2026/2025_05_15_90_Min_Dice_Booster | - | 3 |
| 2026/2026_01_07_Crazy_with_Aces_2_3_4 | - | 4 |
| 2026/2026_01_16_Chance_to_win_Wild_Ordinary | - | 1 |
| 2026/2026_01_19_Chance_to_get_1_out_of_3_Cards | - | 4 |
| 2026/2026_02_03_SS_act_20_Wild_Ace | - | 1 |
| 2026/2026_02_16_Shiny_Show_Wilds | - | 7 |
| 2026/2026_02_20_Shiny_Show_Different Prizes | - | 1 |
| 2026/2026_02_22_SS_Chance_To_Win_Wild_Any | - | 1 |
| 2026/2026_02_23_SS_WIld_Any | - | 1 |
| 2026/2026_02_27_Shiny_Show_Special_Acts | - | 1 |
| 2026/2026_03_14_SS_Different_Prizes | - | 1 |
| 2026/2026_04_11_Ace_Day_Crazy_with_Aces_2_3_4 | - | 4 |
| 2026/2026_05_09_Shiny_Show_Wilds | - | 1 |
| 2026/2026_05_12_JP_Symbol | - | 1 |
| 2026/2026_05_12_SS_Clan_Pack_Moley | - | 2 |
| 2026/2026_05_14_SS_JP_Symbol | - | 1 |
| 2026/2026_05_17_SS_Clan_Pack_Guraranteed | - | 1 |
| 2026/2026_06_14_SS_Aces | - | 1 |
| 2026/2026_06_15_SS_4Stars_Jackpot | - | 2 |
| 2026/2026_06_24_SS_Crazy_With_Aces | - | 4 |
| Joker Promotions/2026_03_09_SS_Joker_Launch | - | 9 |
| Joker Promotions/2026_03_24_SS_All_Cards | - | 1 |
| Joker Promotions/2026_04_08_Different_Prizes | - | 1 |
| Joker Promotions/2026_05_10_SS_Joker_All_Cards | - | 1 |
| Joker Promotions/2026_05_16_Different_Prizes | - | 1 |
| Joker Promotions/2026_07_04_SS_Joker_All_Cards | - | 1 |

