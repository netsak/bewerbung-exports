# Bewerber-Aufgabe AUSU: Exporte konsumieren

Eines der Standard-Probleme im Team AUSU ist das Verarbeiten von Exporten, um
irgendwelche Datenbestände zu aktualisieren. Das kann eine Postgres sein, oder
ein SOLR-Index, oder unsere PLA-Angebote bei Google oder Microsoft, oder...

Exporte sind Dateien mit Angeboten. Es gibt dabei zwei Typen solcher Dateien,
bases und deltas. Bases enthalten *alle* Angebote, Deltas nur geänderte
Angebote (also Updates, Deletes und Inserts).

Das Verzeichnis `exports/` enthält ein paar beispielhafte Export-Dateien (Bases
und Deltas).

Die Bewerber-Aufgabe besteht nun darin, diese Exporte sinnvoll zu konsumieren
und die Angebote in `DOCS` stets aktuell zu halten. Das mitgelieferte
Code-Gerüst ist nur ein Vorschlag und darf umgebaut werden, wenn Du eine
bessere Idee oder andere Vorstellung hast. Es sollte aber immer der
prozessierte Dateiname und der danach vorliegende Dokumentenstand ausgegeben
werden.
