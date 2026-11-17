# Schriften der CK3-Chronik: Herkunft und Lizenz

Beide Schriften stehen unter der **SIL Open Font License, Version 1.1**. Die Lizenztexte mit den Urhebervermerken liegen daneben (`OFL-Texturina.txt`, `OFL-EBGaramond.txt`), so wie sie im Repo der Quelle stehen. Keine der beiden nennt einen „Reserved Font Name“; verkleinerte und umgewandelte Fassungen dürfen den Namen deshalb behalten.

| Schrift | Verwendung | Urheber | Fassung |
|---|---|---|---|
| Texturina | Titel, Rubriken, Initialen (Textura) | Copyright 2020 The Texturina Project Authors (https://github.com/Omnibus-Type/Texturina); Entwurf Guillermo Torres, Omnibus-Type | Version 1.002, variabel (Strichstärke 100–900, optische Größe 12–72) |
| EB Garamond | Lesetext, gerade und kursiv | Copyright 2017 The EB Garamond Project Authors (https://github.com/octaviopardo/EBGaramond12) | Version 1.003, variabel (Strichstärke 400–800) |

## Quelle

Geladen am 17.11.2026 aus dem Repo von Google Fonts, `github.com/google/fonts`, Stand `7af0d90b4d532ffa4b041937b560c6df4e7b1e95` (16.11.2026):

| Original | SHA-256 |
|---|---|
| `ofl/texturina/Texturina[opsz,wght].ttf` | `478a15d7145cf94565cfc1aeb33596aeb0118c7d86a84d061ddf46de3d7dfda3` |
| `ofl/ebgaramond/EBGaramond[wght].ttf` | `ef9512f92f6d579e5dc75af59a5a4b1b8b47d2eda89e00b954d44520e5369027` |
| `ofl/ebgaramond/EBGaramond-Italic[wght].ttf` | `bba2c4499c93c9612b90b9825d32b07da52fce2fe57562a1eb6b833553f93c4e` |
| `ofl/texturina/OFL.txt` | `631ba6504ec2454e472196173aea91c423295787d2128f3732e73fb07a9ea1e0` |
| `ofl/ebgaramond/OFL.txt` | `0985066662eb755ed3683ae5482a81a9195b49ce3f7e165cc2388b3dbece7dd7` |

## Dateien im Repo

Gebaut mit `scripts/schriften.py` (fontTools 4.67.0). Die Prüfung des Repos (`scripts/validate-data.mjs`) vergleicht jede Schriftdatei mit der Prüfsumme hier.

| Datei | Zeichen | Bytes | SHA-256 |
|---|---|---|---|
| `texturina.woff2` | 608 | 112384 | `fca8ade0a00a833ff4fbfec0607a491b21e58b170928a9af7258ff3126b22189` |
| `eb-garamond.woff2` | 1071 | 138532 | `93a9521d90014c2026c22e4cda31f86efe1b4fb1cd5e918372796270d97fa8e3` |
| `eb-garamond-italic.woff2` | 1058 | 139584 | `f4967faeffc8ade2f2c1a799513f87e262a85c79a28a1f51a0605a753f66c1ec` |
| `OFL-Texturina.txt` | | 4393 | `631ba6504ec2454e472196173aea91c423295787d2128f3732e73fb07a9ea1e0` |
| `OFL-EBGaramond.txt` | | 4398 | `0985066662eb755ed3683ae5482a81a9195b49ce3f7e165cc2388b3dbece7dd7` |

## Was gegenüber den Originalen geändert ist

1. **Zeichenvorrat:** auf lateinische Schrift verkleinert (Latin-1, Latin Extended-A und -B, Latin Extended Additional, Modifikatoren, kombinierende Akzente, Satzzeichen, Zahlzeichen, Währung). Das deckt die Namen aller Kulturen im deutschen Text von Crusader Kings III 1.21 in lateinischer Schrift. Griechisch, Kyrillisch und die Lautschrift der EB Garamond sind weggelassen.
2. **Format:** WOFF2 ohne Hinting.
3. **Kapitälchen in EB Garamond (gerade):** In deutschem Text ersetzt die Schrift f, Ä, Ö und Ü durch eigene Formen, für die das Original kein Kapitälchen kennt; in einer Kapitälchenzeile blieb das f klein. Ergänzt sind vier Zuordnungen: `f.DEU → f.sc`, `Adieresis.deu → Adieresis.sc`, `Odieresis.deu → Odieresis.sc`, `Udieresis.deu → Udieresis.sc`.

Die Namenseinträge der Dateien nennen weiter Urheber und Lizenz („This Font Software is licensed under the SIL Open Font License, Version 1.1.“). `py -3 scripts/schriften.py --pruefen` liest sie aus den Dateien und bricht ab, wenn die Lizenz fehlt.
