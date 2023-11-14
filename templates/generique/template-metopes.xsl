<?xml version="1.0" encoding="UTF-8"?>
<!-- Développée par Yves Marcoux. Licence en préparation - Tous droits réservés.
  XSLT développée pour exporter vers TEI MétopesOE des articles stylo
  convertis en TEI par pandoc.
2020-12-18: v0 Version préliminaire.
2022-03-05: v1 Ajustements divers pour suivre l’évolution du format cible.
2022-11-01: v1 Prise en compte de la nouvelle structure de dossiers cible pour MétopesOE.
2022-12-02: v1 Ajustements mineurs.
2023-06-12: v1 Inclusion de nouvelles métadonnées (issue 41) + prise en charge du nouveau
  template TEI passé à pandoc.
2023-09-13: Corrigé typo "||" => "|" (ligne 382).
2023-09-27: Ajouté namespace "stylo:" pour subtitle_f (ligne 100).
2023-09-27: indent="no" (au lieu de "yes").
2023-09-27: div[@type='bibliography'] au lieu de div[@type='bibliographie'].
2023-09-28: Remplacer les seg[@type="code"] par des <code>.
2023-09-28: Éliminer un <p> intermédiaire lorsque seul dans un <item>.
2023-09-29: Ajouté TEI/@change="commons_edition" dans l’export.
2023-10-13: (Antoine Fauchié): Élimination de <seriesStmt> de l’extrant.
2023-10-16 et 17: Plusieurs ajouts / modifications pour se conformer le mieux possible au
  schéma RNG et aux exemples nouvellement reçus, de même qu’à la discussion sur HNGitlab
  https://gitlab.huma-num.fr/ecrinum/stylo/vers-metopes/-/issues/8#note_80760
  qui permettent de se faire une meilleure idée de ce que sera métopesoe à moyen terme.
-->
<xsl:stylesheet version="2.0" xpath-default-namespace="http://www.tei-c.org/ns/1.0"
  xmlns="http://www.tei-c.org/ns/1.0" xmlns:stylo="http://stylo.huma-num.fr/ns/1.0"
  xmlns:ym="http://www.marcouxmedias.com" xmlns:xs="http://www.w3.org/2001/XMLSchema"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" exclude-result-prefixes="#all">

  <xsl:output method="xml" version="1.0" indent="no" encoding="UTF-8"
    omit-xml-declaration="no"/>

  <xsl:function name="ym:lastIndexOf" as="xs:integer">
    <xsl:param name="str" />
    <xsl:param name="car" />
    <xsl:sequence select="if (contains($str, $car)) then
      max(for $i in (1 to string-length($str)) return
      if (substring($str, $i, 1) = $car) then $i else 0)
      else 0" />
  </xsl:function>

  <xsl:variable name="styloData" select="/TEI/teiHeader/xenoData/stylo:stylo-metadata"/>
  <xsl:variable name="biblioLikeDivs" select="/TEI/text/body/div
    [contains(@xml:id, 'biblio') or contains(@xml:id, 'citation') or
      ends-with(normalize-space(@xml:id), 'graphie')]" />
  <xsl:variable name="moveToBack" select="$biblioLikeDivs |
    /TEI/text/body/div[contains(@xml:id, 'biographi')]"/>

  <xsl:template match="/">
<!--    <xsl:comment>Ceci est le document output.</xsl:comment>-->
    <xsl:apply-templates select="*"/>
  </xsl:template>

  <xsl:template match="TEI">
    <xsl:copy>
      <xsl:attribute name="change" select="'commons_edition'" />
      <xsl:apply-templates select="@*, node()" />
    </xsl:copy>
  </xsl:template>

  <xsl:template match="teiHeader">
    <teiHeader>
      <xsl:apply-templates select="fileDesc"/>
      <profileDesc>

        <langUsage>
          <xsl:for-each select="//@xml:lang">
            <language ident="{.}"/>
          </xsl:for-each>
        </langUsage>

        <textClass>
          <xsl:variable name="myChunk" select=
            "$styloData/stylo:kwList[stylo:lang = 'fr']"/>
          <xsl:if test="$myChunk">
            <keywords scheme="keyword" xml:lang="fr">
              <list type="unordered">
                <xsl:for-each select="tokenize($myChunk/stylo:list, ',')">
                  <item><xsl:value-of select="normalize-space()"/></item>
                </xsl:for-each>
              </list>
            </keywords>
          </xsl:if>
          <xsl:variable name="myChunk" select=
            "$styloData/stylo:kwList[stylo:lang = 'en']"/>
          <xsl:if test="$myChunk">
            <keywords scheme="keyword" xml:lang="en">
              <list type="unordered">
                <xsl:for-each select="tokenize($myChunk/stylo:list, ',')">
                  <item><xsl:value-of select="normalize-space()"/></item>
                </xsl:for-each>
              </list>
            </keywords>
          </xsl:if>
          <xsl:if test="$styloData/stylo:controlledKeyword">
            <keywords scheme="Rameau" xml:lang="fr">
              <list type="unordered">
                <xsl:for-each
                  select="$styloData/stylo:controlledKeyword">
<!-- <item source="{stylo:uriRameau}"> 2023-10-16 @source maintenant interdit. -->
                  <item>
                    <xsl:value-of select="stylo:label"/>
                  </item>
                </xsl:for-each>
              </list>
            </keywords>
          </xsl:if>
        </textClass>

      </profileDesc>

      <encodingDesc>
        <tagsDecl>
          <rendition scheme="css" xml:id="list-decimal">list-style-type:decimal;</rendition>
          <rendition scheme="css" xml:id="list-lower-roman">list-style-type:lower-roman;</rendition>
          <rendition scheme="css" xml:id="list-upper-roman">list-style-type:upper-roman;</rendition>
          <rendition scheme="css" xml:id="list-lower-alpha">list-style-type:lower-alpha;</rendition>
          <rendition scheme="css" xml:id="list-upper-alpha">list-style-type:upper-alpha;</rendition>
          <rendition scheme="css" xml:id="list-square">list-style-type:square;</rendition>
          <rendition scheme="css" xml:id="list-circle">list-style-type:circle;</rendition>
          <rendition scheme="css" xml:id="list-disc">list-style-type:disc;</rendition>
        </tagsDecl>
      </encodingDesc>

    </teiHeader>
  </xsl:template>

  <xsl:template match="titleStmt">
    <titleStmt>
      <title type="main">
        <xsl:apply-templates select="$styloData/stylo:title/node()"/>
      </title>
      <xsl:if test="$styloData/stylo:subtitle">
        <title type="sub">
          <xsl:apply-templates select="$styloData/stylo:subtitle/node()"/>
        </title>
      </xsl:if>
      <xsl:for-each select="$styloData/stylo:translatedTitle">
        <title type="trl" xml:lang="{stylo:lang}">
          <xsl:apply-templates select="stylo:text/node()"/>
        </title>
      </xsl:for-each>
      <xsl:apply-templates select="$styloData/stylo:author"/>
      <xsl:apply-templates select="$styloData/stylo:translator"/>
    </titleStmt>
    <editionStmt>
      <edition>
        <date>
          <xsl:value-of select="translate($styloData/stylo:date, '/', '-')"/>
        </date>
      </edition>
    </editionStmt>
  </xsl:template>

  <xsl:template match="publicationStmt">
    <publicationStmt>
      <xsl:choose> <!-- Test requis pour HN-02, qui n’a pas de publisher. -->
        <xsl:when test="publisher">
          <xsl:copy-of select="publisher" />
        </xsl:when>
        <xsl:otherwise>
          <p>Éditeur non précisé.</p>
        </xsl:otherwise>
      </xsl:choose>
    </publicationStmt>
<!-- 2023-10-13 (Antoine Fauchié) Pour le moment, le nom de la revue et/ou le numéro de la
  livraison semblent absents de métopesoe…
    <xsl:if test="$styloData/stylo:journal_issue | $styloData/stylo:journal">
      <seriesStmt>
        <title level="j">
-->
<!-- Un <title> doit précéder <idno> dans l’extrant, sinon invalide.
En l’absence de "journal", nous mettrons donc un <title> vide. -->
<!--
    <xsl:apply-templates select="$styloData/stylo:journal/node()" />
        </title>
        <xsl:if test="$styloData/stylo:journal_issue">
          <idno type="journal_issue">
            <xsl:apply-templates select="$styloData/stylo:journal_issue/node()" />
          </idno>
        </xsl:if>
      </seriesStmt>
    </xsl:if>
-->
<!-- 2023-10-16 Semble absent de métopesoe… À clarifier vs translatedTitle du côté stylo.
    <xsl:variable name="transOf" select="$styloData/stylo:translationOf"/>
    <xsl:if test="$transOf">
        <notesStmt>
          <relatedItem type="translationOf" target="{$transOf/stylo:url}">
            <bibl>
              <title><xsl:apply-templates select="$transOf/stylo:title/node()" /></title>
              <lang><xsl:apply-templates select="$transOf/stylo:lang/node()" /></lang>
            </bibl>
          </relatedItem>
        </notesStmt>
      </xsl:if>
-->
  </xsl:template>

  <xsl:template match="sourceDesc">
    <sourceDesc>
      <p>Conversion XSLT Stylo → TEI Commons (métopes)</p>
      <p>développée par Yves MARCOUX, marcouxmedias.com</p>
      <!-- <xsl:value-of
    select="translate(substring(string(current-dateTime()), 1, 16), 'T', ' ')"/> -->
      <p>Version TEI Commons (métopes) : Meilleure approximation en date du 2023-10-17</p>
    </sourceDesc>
  </xsl:template>

  <xsl:template match="stylo:translator">
    <xsl:if test="normalize-space()">
      <editor role="trl">
        <persName>
          <forename><xsl:apply-templates select=
            "stylo:forname/node() | stylo:forename/node()"
            /></forename>
          <surname><xsl:apply-templates select="stylo:surname/node()"/></surname>
        </persName>
      </editor>
    </xsl:if>
  </xsl:template>

  <xsl:template match="stylo:author">
    <xsl:if test="normalize-space()">
      <author role="aut">
        <persName>
          <forename><xsl:apply-templates select=
            "stylo:forname/node() | stylo:forename/node()"
            /></forename>
          <surname><xsl:apply-templates select="stylo:surname/node()"/></surname>
        </persName>
        <xsl:if test="stylo:affiliations">
          <affiliation><orgName>
            <xsl:apply-templates select="stylo:affiliations/node()"/>
          </orgName></affiliation>
        </xsl:if>
        <xsl:if test="normalize-space(stylo:email)">
          <email>
            <xsl:value-of select="stylo:email"/>
          </email>
        </xsl:if>
        <xsl:if test="normalize-space(stylo:orcid)">
          <idno type="ORCID">
            <xsl:value-of select="stylo:orcid"/>
          </idno>
        </xsl:if>
        <xsl:if test="normalize-space(stylo:isni)">
          <idno type="ISNI">
            <xsl:value-of select="stylo:isni"/>
          </idno>
        </xsl:if>
        <xsl:if test="normalize-space(stylo:viaf)">
          <idno type="VIAF">
            <xsl:value-of select="stylo:viaf"/>
          </idno>
        </xsl:if>
        <xsl:if test="normalize-space(stylo:foaf)">
          <idno type="FOAF">
            <xsl:value-of select="stylo:foaf"/>
          </idno>
        </xsl:if>
      </author>
    </xsl:if>
  </xsl:template>

  <xsl:template match="text">
    <text>
      <xsl:attribute name="xml:id" select="'text'"/>
      <front>

        <div type="titlePage">
<!-- 2023-10-16 Remplacement de titlePage par cette div du côté de métopesoe. -->
          <p rend="title-main">
            <xsl:apply-templates select="$styloData/stylo:title_f/node()"/>
          </p>
          <xsl:for-each select="$styloData/stylo:translatedTitle">
            <p rend="title-trl" xml:lang="{stylo:lang}">
              <xsl:apply-templates select="stylo:text/node()"/>
            </p>
          </xsl:for-each>
          <xsl:if test="$styloData/subtitle">
            <p rend="title-sub">
              <xsl:apply-templates select="$styloData/stylo:subtitle_f/node()"/>
            </p>
          </xsl:if>
          <xsl:for-each select="$styloData/stylo:author[normalize-space()]">
            <p rend="author-aut">
              <xsl:apply-templates select=
                "stylo:forname/node() | stylo:forename/node()"/>
              <xsl:text> </xsl:text>
              <xsl:apply-templates select="stylo:surname/node()"/>
            </p>
            <xsl:if test="normalize-space(stylo:affiliations)">
              <p rend="authority_affiliation">
                <xsl:apply-templates select="stylo:affiliations/node()"/>
              </p>
            </xsl:if>
            <xsl:if test="normalize-space(stylo:email)">
              <p rend="authority_mail">
                <xsl:value-of select="stylo:email"/>
              </p>
            </xsl:if>
          </xsl:for-each>
          <xsl:if test="normalize-space($styloData/stylo:translator)">
            <p rend="editor-trl">
              <xsl:apply-templates select=
                  "stylo:forname/node() | stylo:forename/node()"/>
              <xsl:text> </xsl:text>
              <xsl:apply-templates select="stylo:surname/node()"/>
            </p>
          </xsl:if>

        </div>

        <xsl:variable name="myChunk" select=
          "$styloData/stylo:abstract[stylo:lang = 'fr']"/>
        <xsl:if test="$myChunk">
          <div type="abstract" xml:lang="fr">
            <p><xsl:apply-templates select="$myChunk/stylo:text_f/node()" /></p>
          </div>
        </xsl:if>

        <xsl:variable name="myChunk" select=
          "$styloData/stylo:kwList[stylo:lang = 'fr']"/>
        <xsl:if test="$myChunk">
          <div type="keywords" xml:lang="fr">
            <p><xsl:value-of select="normalize-space($myChunk/stylo:list)"/></p>
          </div>
        </xsl:if>

        <xsl:variable name="myChunk" select=
          "$styloData/stylo:abstract[stylo:lang = 'en']"/>
        <xsl:if test="$myChunk">
          <div type="abstract" xml:lang="en">
            <p><xsl:apply-templates select="$myChunk/stylo:text_f/node()" /></p>
          </div>
        </xsl:if>

        <xsl:variable name="myChunk" select=
          "$styloData/stylo:kwList[stylo:lang = 'en']"/>
        <xsl:if test="$myChunk">
          <div type="keywords" xml:lang="en">
            <p><xsl:value-of select="normalize-space($myChunk/stylo:list)"/></p>
          </div>
        </xsl:if>

        <xsl:if test="$styloData/stylo:acknowledgements">
          <div type="ack">
            <p><xsl:apply-templates select=
              "$styloData/stylo:acknowledgements/node()" /></p>
          </div>
        </xsl:if>

      </front>
      <xsl:apply-templates />
    </text>
  </xsl:template>

  <xsl:template match="stylo:*">
<!-- Template pour transférer certains éléments de stylo (dans xenodata) vers le ns TEI.
Filet de sécurité pour signaler des cas problèmes. -->
<!-- Les ref ne sont pas un problème. -->

    <xsl:if test="not(index-of(('ref'), local-name()))">
      <xsl:message select="concat(document-uri(/), ' ', local-name())"
        > élément inattendu de stylo !</xsl:message>
    </xsl:if>
    <xsl:element name="{local-name()}" namespace="http://www.tei-c.org/ns/1.0">
      <xsl:apply-templates select="@* | node()"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="@xml:id | @target[starts-with(., '#')]">
    <!-- Vérifier si c'est nécessaire, ou si c'est une erreur dans SP1436. -->
    <xsl:attribute name="{name()}" select="translate(., '/:', '__')"/>
  </xsl:template>

  <xsl:template match="@*">
    <xsl:copy-of select="."/>
  </xsl:template>

  <xsl:template match="milestone[normalize-space(@type)='separator']">
    <p rend="break" />
  </xsl:template>

  <xsl:template match="*">
<!-- Template par défaut qui ne fait que reproduire l'élément, tout en permettant d'agir
sur le contenu. Traite (entre autres ?) les p enfants de note, et parfois de quote. -->
    <xsl:copy>
      <xsl:apply-templates select="@* | node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="$biblioLikeDivs//formula[
      @notation = 'TeX' and (. = '^{e}' or . = '^e' or .='^{\textrm{e}}')]">
    <hi rend="sup">e</hi>
<!-- Modifier plutôt le protocole de rédaction ? -->
  </xsl:template>

  <xsl:template match="hi | stylo:hi">
    <hi>
      <xsl:choose>
        <xsl:when test="@rendition = 'simple:italic'">
          <xsl:attribute name="rend" select="'italic'"/>
        </xsl:when>
        <xsl:when test="@rendition = 'simple:superscript'">
          <xsl:attribute name="rend" select="'sup'"/>
        </xsl:when>
        <xsl:when test="@rendition = 'simple:bold'">
          <xsl:attribute name="rend" select="'bold'"/>
        </xsl:when>
        <xsl:when test="@rendition = 'simple:subscript'">
          <xsl:attribute name="rend" select="'sub'"/>
        </xsl:when>
        <xsl:when test="@rendition = 'simple:smallcaps'">
          <xsl:attribute name="rend" select="'small-caps'"/>
        </xsl:when>
        <xsl:when test="@rendition = 'simple:strikethrough'">
          <xsl:attribute name="rend" select="'strikethrough'"/>
        </xsl:when>
      </xsl:choose>
      <xsl:apply-templates select="node()"/>
    </hi>
  </xsl:template>

  <xsl:template match="quote[p]">
    <xsl:if test="*[not(self::p)]">
       <xsl:message
         select="concat(document-uri(/), ' Contenu inattendu dans un quote : ',
          name(*[not(self::p)][1]))" />
    </xsl:if>
    <cit><quote>
<!-- Nous traitons séparément les cas où il y a exactement un seul p comme contenu
et les autres. -->
      <xsl:choose>
        <xsl:when test="(count(*) = 1) and not(text()[normalize-space()])">
<!-- On élimine le <p> comme intermédiaire sous le <quote> : -->
            <xsl:apply-templates select="@*, p/node()" />
<!-- 2023-10-17 On reproduit les attributs du <quote>. -->
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates select="@*, node()" />
        </xsl:otherwise>
      </xsl:choose>
    </quote></cit>
  </xsl:template>

  <xsl:template match=
    "item[p and (count(*) = 1) and not(text()[normalize-space()])]">
<!-- 2023-09-28 Éliminer un <p> intermédiaire lorsque seul dans un <item>. -->
    <item>
      <xsl:apply-templates select="@*, p/node()" />
<!-- 2023-10-16 On reproduit les attributs de l’item; e.g.
  @n parfois utilisé pour commencer une liste à ≠ 1. -->
    </item>
  </xsl:template>

  <xsl:template match="stylo:p">
<!-- On strip simplement les balises.
Requis car SP1376 a des guillemets superflus autour des
résumés (abstract) français, qui cause semble-t-il l’insertion d’un niveau <p>.
À vérifier si c'est utile / nécessaire, peut-être un changement dans le
protocole de rédaction serait plus approprié.
Autre point: si certains éléments du YAML, comme justement les abstract, doivent
éventuellement pouvoir comporter plusieurs paragraphes, il faudra contrôler si le
présent template doit être appliqué ou non. -->
    <xsl:apply-templates select="node()" />
  </xsl:template>

  <xsl:template match="quote | stylo:quote"
    >“<xsl:apply-templates select="@* | node()" />”</xsl:template>
<!-- Les quote[p] sont traités par un autre template. -->

  <xsl:template match="body">
    <body>
<!-- <div type="chapitre" xml:id="mainDiv"> -->
      <xsl:apply-templates select=
        "node() except $moveToBack" />
<!--</div>-->
    </body>
    <xsl:variable name="authWithBio" select=
      "$styloData/stylo:author[stylo:biography]" />
    <xsl:if test="$moveToBack | $authWithBio">
<!-- 2023-09-13 YMA correction typo :
  remplacé "||" ci-dessus par "|" (ne causait pas d’erreur). -->
<!-- SP1391 n'a pas de bibliographie. -->
      <back>
        <xsl:apply-templates select="$moveToBack" />
        <xsl:if test="$authWithBio">
          <xsl:variable name="accordNombre" select=
            "if (count($authWithBio) > 1) then 's' else ''"/>
          <div type="section1" xml:id="notice-biographique">
            <head>Notice<xsl:value-of select="$accordNombre"
            /> biographique<xsl:value-of select="$accordNombre"/></head>
          <xsl:for-each select="$authWithBio">
<!-- Pour chaque auteur avec biography, on génére une "biographie" qui
ajoute le nom de l’auteur avant le contenu de biography.
-->
            <p><hi rend="bold"><xsl:apply-templates select=
              "stylo:forename/node() | stylo:forname/node()" />
              <xsl:text> </xsl:text>
              <xsl:apply-templates select="stylo:surname/node()" /> :</hi>
              <xsl:text> </xsl:text>
              <xsl:apply-templates select="stylo:biography/node()" /></p>
          </xsl:for-each>
          </div>
        </xsl:if>
      </back>
    </xsl:if>
  </xsl:template>

  <xsl:template match="$biblioLikeDivs">
    <div type="bibliography">
      <head><xsl:apply-templates select="head[1]/node()"/></head>
      <xsl:apply-templates select="node() except head[1]" />
    </div>
  </xsl:template>

  <xsl:template match="div except $biblioLikeDivs">
    <xsl:variable name="niveau" select="string(count(ancestor-or-self::div))" />
    <div type="section{$niveau}">
      <xsl:apply-templates select="@xml:id" />
      <xsl:apply-templates select="node()" />
    </div>    
  </xsl:template>

  <xsl:template match="head">
<!-- 2022-03-04 <xsl:variable name="niveau" select="string(count(ancestor-or-self::div))" />-->
    <head>
      <xsl:apply-templates select="node()" />
    </head>
  </xsl:template>

  <xsl:template match="p[not(parent::quote | parent::note)]">
    <p>
      <xsl:apply-templates select="node()" />
    </p>
  </xsl:template>

  <xsl:template match="p[figure]" priority="2">
<!--  <xsl:template match="p[figure and (count(*) = 1)]" priority="2">
2022-09-28 Il semble pouvoir y avoir maintenant un ou des <ref> aussi,
donc on ne peut restreindre sur count(*)=1,
par contre, ce cas ne semble se produire qu’avec HN-01 (que j’ai trafiqué en
essai-HN-fictif) et j’ai l’impression qu’il y a une erreur de saisie (manque un saut
de ligne), donc, un protocole de rédaction plus serré serait probablement une meilleure
solution. -->
      <xsl:variable name="numFig" select="1 + count(
      if (./figure intersect $moveToBack//figure) then
      (//figure except $moveToBack//figure) |
      ($moveToBack//figure intersect preceding::figure)
      else
      (preceding::figure except $moveToBack//figure)
      )" />
<!-- Couvre les cas où il y a des figures dans des sections à déplacer en back. -->
    <figure xml:id="fig{$numFig}">
<!-- Vérifier s'il faut le numFig sur 2 chiffres. -->
      <xsl:variable name="url" select="figure[1]/graphic[1]/@url" />
      <graphic url="../icono/br/{if (contains($url, '/')) then
        substring($url, ym:lastIndexOf($url, '/')+1)
        else $url}" />

      <head>Figure <xsl:value-of 
        select="$numFig"/> – <xsl:apply-templates
          select="figure/head/node()" />
      </head>
    </figure>
  </xsl:template>

  <xsl:template match="$biblioLikeDivs/p" priority="2">
    <bibl>
      <xsl:apply-templates select="@xml:id" />
      <xsl:apply-templates select="node()" />
    </bibl>
  </xsl:template>

  <xsl:template match="note">
    <xsl:variable name="numNote" select="1 + count(
      if (. intersect $moveToBack//note) then
        (//note except $moveToBack//note) |
        ($moveToBack//note intersect preceding::note)
      else
      (preceding::note except $moveToBack//note)
      )" />
<!-- Couvre les cas où il y a des notes dans des sections à déplacer en back. -->
    <note n="{$numNote}" place="foot"
      xml:id="ftn{$numNote}">
      <xsl:apply-templates select="node()" />
    </note>
  </xsl:template>

  <xsl:template match="table">
    <xsl:variable name="numTable" select="1 + count(
      if (. intersect $moveToBack//table) then
      (//table except $moveToBack//table) |
      ($moveToBack//table intersect preceding::table)
      else
      (preceding::table except $moveToBack//table)
      )" />
<!-- Couvre les cas où il y a des tables dans des sections à déplacer en back. -->
    <table xml:id="Table{$numTable}"
      cols="{count(row[1]/cell)}"
      rows="{count(row)}">
      <xsl:apply-templates select="node()" />
    </table>
  </xsl:template>

  <xsl:template match="cell/p" priority="2">
<!-- On strip simplement les balises du <p>. -->
    <xsl:apply-templates select="node()" />
  </xsl:template>

  <xsl:template match="seg[@type='code']">
<!-- 2023-09-28 Remplacer par <code>: -->
    <code>
      <xsl:apply-templates select="node()" />
    </code>
  </xsl:template>

  <xsl:template match="list/@type
    [starts-with(normalize-space(.), 'ordered:')]">
<!-- Représenter les listes ordonnées comme métopesoe le veut. -->
    <xsl:attribute name="type" select="'ordered'" />
    <xsl:attribute name="rendition">
      <xsl:variable name="subtype"
        select="normalize-space(substring-after(., ':'))"/>
      <xsl:choose>
        <xsl:when test="$subtype='loweralpha'">
          <xsl:text>#list-lower-alpha</xsl:text>
        </xsl:when>
        <xsl:when test="$subtype='lowerroman'">
          <xsl:text>#list-lower-roman</xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>#list-decimal</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
  </xsl:template>

</xsl:stylesheet>
