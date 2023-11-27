# Chaîne de production de Sens public pour Stylo
_Instructions pour l'implémentation des templates utiles aux exports de Stylo pour la revue Sens public._

La revue _Sens public_ a besoin des exports suivants :

- [x] HTML : basé sur le template `templateHtml5.html5`. Remarque : il faut utiliser les options suivantes dans Pandoc : `--standalone --section-divs --ascii --toc  [option --toc selon le choix sélectionné ou non]`. Le style bibliographique se trouve dans `chicagomodified.csl` ;
- [ ] XTML : basé sur le template `template-xhtml.html`. Remarque : il faut utiliser les options suivantes dans Pandoc : `--standalone --section-divs --ascii --toc  [option --toc selon le choix sélectionné ou non]`. Le style bibliographique se trouve dans `chicagomodified.csl`. **Attention** : ce template sert à produire le XML ; dans le script actuel, pour normaliser les balises HTML, on utilisait les _regex_ suivantes (il est possible que ces opérations ne soient plus nécessaires, tout dépend de la version de Pandoc, **il faut tester la conversion Pandoc avant d'intégrer ces regex**) :
    - `sed -i -e "s/NonBreakingSpace/nbsp/g" ${GET[id]}.html`
    - `sed -i -e "s/rsquor;/#8217;/g" ${GET[id]}.html`
    - `sed -i -e "s/OpenCurlyDoubleQuote/ldquo/g" ${GET[id]}.html`
    - `sed -i -e "s/<em><\/em>//g" ${GET[id]}.html`
    - `sed -i -e "s/NonBreakingSpace/nbsp/g" ${GET[id]}.xhtml`
    - `sed -i -e "s/rsquor;/#8217;/g" ${GET[id]}.xhtml`
    - `sed -i -e "s/OpenCurlyDoubleQuote/ldquo/g" ${GET[id]}.xhtml`
    - `sed -i -e "s/<em><\/em>//g" ${GET[id]}.xhtml`
- [x] PDF : basé sur le template `templateLaTeX.latex` (sources to tex to PDF). Les options à appliquer : `--standalone --toc [selon l'option sélectionnée ou non]`. Ce template utilise des médias (logos, etc.) qui se trouvent dans `templates/sens-public/medias`. Ce fichier était normalement créé en faisant d'abord un Pandoc vers Tex et ensuite en appelant XeLaTeX (2 fois, pour la génération d'un index…), si ça marche directement depuis Pandoc tant mieux : à tester ;
- [ ] XMLT Érudit : transformation XSLT à partir du fichier XHTML et avec la feuille de transformation `template-erudit.xsl`, et qui fonctionne avec Saxon avec la commande suivante : `java  -cp /usr/local/vendor/saxon9he.jar:/usr/local/vendor/tagsoup-1.2.1.jar net.sf.saxon.Transform -x:org.ccil.cowan.tagsoup.Parser -s:${GET[id]}.html -xsl:../templates/template-erudit.xsl -o:${GET[id]}.erudit.xml !indent=yes`. Ensuite il y a un autre script `script-idifier.sh` qui effectue des modifications pour les tableaux. Le fichier tagsoup-1.2.1.jar est également dans le dossier.
