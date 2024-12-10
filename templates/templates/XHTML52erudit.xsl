<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xsl:stylesheet [ <!ENTITY NonBreakingSpace "&#160;"> ]>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:h="http://www.w3.org/1999/xhtml"
  exclude-result-prefixes="h" version="2.0" xpath-default-namespace="http://www.w3.org/1999/xhtml"
  xmlns="http://www.erudit.org/xsd/article">

<!-- TODO
  - [x] gestion br (voir branche dédiée)
    - dirty solution, si intéressé, intégrer la solution https://stackoverflow.com/questions/54584969/xslt-in-a-p-element-how-to-replace-a-line-break-br-with-successive-ali
  - [x] ajouter les num de dossier > solution commentée pour aller les chercher dans un fichier externe
  - [x] ajouter les ordseq > solution commentée pour aller les chercher dans un fichier externe


    ## Droits d'auteur
	- deuxième balise droitauteur (lien vers licence) non gérée

    ## Mots-clés (invalide)
          - [ ] gérer automatiquement les langues

    ## autres contributions : réviseur ?

    ## intégrer un test dans le script pour transformer iframe en <objet typeobj="video">

    ## Tableau XML mal formé(invalide)
        ● articles [x] 1291, [x] 1335, [x] 1348
        - voir spec :
            - tableaux : http://retro.erudit.org/documentation/balisage/tableauxTextuels.html
            - type 5 : http://retro.erudit.org/documentation/balisage/ttat5.html

    ## Figures
-->

  <xsl:variable name="idArticle" select="substring-before(substring-after(base-uri(),'Edition/./SP'),'/')" />

  <xsl:template match="/">
    <article xmlns:xlink="http://www.w3.org/1999/xlink"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xmlns="http://www.erudit.org/xsd/article"
      xsi:schemaLocation="http://www.erudit.org/xsd/article http://www.erudit.org/xsd/article/3.0.0/eruditarticle.xsd"
      qualtraitement="complet" idproprio="">
      <xsl:choose>
        <xsl:when
        test="contains('essai sommaire', html/head/meta[normalize-space(@name) = 'prism.genre']/lower-case(normalize-space(@content)))">
          <xsl:attribute name="typeart">article</xsl:attribute>
        </xsl:when>
        <xsl:when
          test="contains('lecture', html/head/meta[normalize-space(@name) = 'prism.genre']/lower-case(normalize-space(@content)))">
          <xsl:attribute name="typeart">compterendu</xsl:attribute>
        </xsl:when>
       <xsl:otherwise>
          <xsl:attribute name="typeart">autre</xsl:attribute>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:attribute name="lang">
        <xsl:value-of select="html/head/meta[normalize-space(@name) = 'DC.language']/@content"/>
      </xsl:attribute>
      <xsl:for-each select="html/body//div[normalize-space(@resource) = '#issue']">
        <xsl:choose>
          <xsl:when test="(span[normalize-space(@class) = 'titreDossier'] = 'varia') or (span[normalize-space(@class) = 'titreDossier'] = 'Varia') or (span[normalize-space(@class) = 'titreDossier'] = '')">
            <xsl:attribute name="horstheme">
              <xsl:value-of>oui</xsl:value-of>
            </xsl:attribute>
          </xsl:when>
          <xsl:otherwise>
            <!-- transfo locale avec le sommaire -->
            <!-- <xsl:attribute name="idref">th<xsl:value-of select="document('/home/nicolas/gitlab/SP-articles/Edition/sommaire2018.xml')/*:sommaire/*:article[@id=$idArticle]/@dossier"/></xsl:attribute> -->
            <!-- transfo stylo-export -->
            <xsl:attribute name="idref">thXXXX</xsl:attribute>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:for-each>
      <!-- transfo locale avec le sommaire -->
      <!-- <xsl:attribute name="ordseq"><xsl:value-of select="document('/home/nicolas/gitlab/SP-articles/Edition/sommaire2018.xml')/*:sommaire/*:article[@id=$idArticle]/@ordseq"/></xsl:attribute> -->
      <!-- transfo stylo-export -->
      <xsl:attribute name="ordseq">##</xsl:attribute>

      <admin>
        <infoarticle>
          <xsl:for-each select="html/body//div[normalize-space(@class) = 'keywords']">
            <grdescripteur>
              <xsl:attribute name="lang">
                <xsl:value-of select="//meta[normalize-space(@name) = 'DC.language']/@content"/>
              </xsl:attribute>
              <xsl:if test=".//span[normalize-space(@class) = 'idRameau']">
                <xsl:attribute name="scheme">http://rameau.bnf.fr</xsl:attribute>
              </xsl:if>
              <xsl:for-each select="./div">
                <descripteur>
                  <xsl:apply-templates select="span[normalize-space(@class) = 'label']"/>
                </descripteur>
              </xsl:for-each>
            </grdescripteur>
          </xsl:for-each>
          <nbpara>
            <xsl:value-of
              select="
                count(.//p[not(ancestor::div[
                contains(' figure references footnotes ',
                concat(' ', normalize-space(@class), ' '))
                ])])"
            />
          </nbpara>
          <nbmot>
            <xsl:variable name="temp" select="tokenize(string-join(.//p, ' '), '\s+')"/>
            <xsl:value-of select="count($temp)"/>
          </nbmot>
          <nbfig>
            <xsl:value-of select="count(.//figure)"/>
          </nbfig>
          <nbtabl>
            <xsl:value-of select="count(.//table)"/>
          </nbtabl>
          <nbaudio>
            <xsl:value-of select="count(.//audio)"/>
          </nbaudio>
          <nbvideo>
            <xsl:value-of select="count(.//video)"/>
          </nbvideo>
          <nbrefbiblio>
            <xsl:value-of select="count(.//div[normalize-space(@class) = 'references']/div)"/>
          </nbrefbiblio>
          <nbnote>
            <xsl:value-of select="count(.//section[normalize-space(@class) = 'footnotes']/ol/li)"/>
          </nbnote>
        </infoarticle>

	<!-- id de revue à adapter -->
        <revue id="sp02131" lang="fr">
          <titrerev>
            <xsl:value-of select="html/head/meta[normalize-space(@name) = 'DC.source']/@content"/>
          </titrerev>
	<!-- abbr de revue à adapter -->
          <titrerevabr>sp</titrerevabr>
          <idissnnum>
            <xsl:value-of
              select="html/head/meta[normalize-space(@name) = 'DC.identifier' and normalize-space(@class) = 'issn']/@content"
            />
          </idissnnum>


          <xsl:for-each
            select="html/body/div[normalize-space(@class) = 'indexations-foaf']//div[normalize-space(@class) = 'foaf-director']">
            <directeur>
              <xsl:if test="span[normalize-space(@property) = 'gender'] = 'male'">
                <xsl:attribute name="sexe">
                  <xsl:value-of>masculin</xsl:value-of>
                </xsl:attribute>
              </xsl:if>
              <xsl:if test="span[normalize-space(@property) = 'gender'] = 'female'">
                <xsl:attribute name="sexe">
                  <xsl:value-of>feminin</xsl:value-of>
                </xsl:attribute>
              </xsl:if>
              <nompers>
                <prenom>
                  <xsl:value-of select="span[normalize-space(@property) = 'firstName']"/>
                </prenom>
                <nomfamille>
                  <xsl:apply-templates select="span[normalize-space(@property) = 'familyName']"/>
                </nomfamille>
              </nompers>
            </directeur>
          </xsl:for-each>

          <xsl:if
            test="html/body/div[normalize-space(@class) = 'indexations-foaf']//div[normalize-space(@class) = 'foaf-redactor']/span[normalize-space(@property) = 'firstName']/text()">
            <xsl:for-each
              select="html/body/div[normalize-space(@class) = 'indexations-foaf']//div[normalize-space(@class) = 'foaf-redactor']">
              <redacteurchef typerc="invite">
                <xsl:if test="span[normalize-space(@property) = 'gender'] = 'male'">
                  <xsl:attribute name="sexe">
                    <xsl:value-of>masculin</xsl:value-of>
                  </xsl:attribute>
                </xsl:if>
                <xsl:if test="span[normalize-space(@property) = 'gender'] = 'female'">
                  <xsl:attribute name="sexe">
                    <xsl:value-of>feminin</xsl:value-of>
                  </xsl:attribute>
                </xsl:if>
                <!-- transfo locale avec le sommaire -->
                <!-- <xsl:attribute name="idrefs">th<xsl:value-of select="document('/home/nicolas/gitlab/SP-articles/Edition/sommaire2018.xml')/*:sommaire/*:article[@id=$idArticle]/@dossier"/></xsl:attribute> -->
                <!-- transfo stylo-export -->
                <xsl:attribute name="idrefs">thXXXX</xsl:attribute>
                <nompers>
                  <prenom>
                    <xsl:value-of select="span[normalize-space(@property) = 'firstName']"/>
                  </prenom>
                  <nomfamille>
                    <xsl:apply-templates select="span[normalize-space(@property) = 'familyName']"/>
                  </nomfamille>
                </nompers>
              </redacteurchef>
            </xsl:for-each>
          </xsl:if>

        </revue>

        <numero id="">
          <pub>
            <annee>
              <xsl:value-of
                select="html/head/meta[normalize-space(@name) = 'DC.date' and normalize-space(@class) = 'year']/@content"/>
            </annee>
          </pub>
          <pubnum>
            <date typedate="publication">
              <xsl:value-of
                select="html/head/meta[normalize-space(@name) = 'DC.date' and normalize-space(@class) = 'completeDate']/@content"/>
            </date>
          </pubnum>
          <xsl:for-each select="html/body//div[normalize-space(@resource) = '#issue']">
          <xsl:if test="(span[normalize-space(@class) = 'titreDossier'] != 'varia') and (span[normalize-space(@class) = 'titreDossier'] != 'Varia') and (span[normalize-space(@class) = 'titreDossier'] != '')">
          <grtheme>
            <!-- transfo locale avec le sommaire -->
            <!-- <xsl:attribute name="id">th<xsl:value-of select="document('/home/nicolas/gitlab/SP-articles/Edition/sommaire2018.xml')/*:sommaire/*:article[@id=$idArticle]/@dossier"/></xsl:attribute> -->
            <!-- transfo stylo-export -->
            <xsl:attribute name="id">thXXXX</xsl:attribute>
            <theme><xsl:value-of select="span[normalize-space(@class) = 'titreDossier']"/></theme>
          </grtheme>
          </xsl:if>
          </xsl:for-each>
        </numero>
        <editeur>
          <nomorg>
            <xsl:value-of
              select="html/head/meta[normalize-space(@name) = 'DC.publisher' and normalize-space(@class) = 'editeur']/@content"
            />
          </nomorg>
        </editeur>
        <prod>
          <nomorg>
            <xsl:value-of
              select="html/head/meta[normalize-space(@name) = 'DC.publisher' and normalize-space(@class) = 'producteur']/@content"
            />
          </nomorg>
        </prod>
        <prodnum>
          <nomorg>
            <xsl:value-of
              select="html/head/meta[normalize-space(@name) = 'DC.publisher' and normalize-space(@class) = 'producteurNum']/@content"
            />
          </nomorg>
        </prodnum>
        <diffnum>
          <nomorg>
            <xsl:value-of
              select="html/head/meta[normalize-space(@name) = 'DC.publisher' and normalize-space(@class) = 'diffuseur']/@content"
            />
          </nomorg>
        </diffnum>
        <schema nom="Erudit Article" version="3.0.0" lang="fr"/>
        <droitsauteur>
          <xsl:value-of select="html/head/meta[normalize-space(@name) = 'DC.rights']/@content"/>
          <nomorg><xsl:value-of
            select="html/head/meta[normalize-space(@name) = 'DC.publisher' and normalize-space(@class) = 'producteur']/@content"/></nomorg>, <xsl:value-of
            select="html/head/meta[normalize-space(@name) = 'DC.date' and normalize-space(@class) = 'year']/@content"/>
        </droitsauteur>
        <droitsauteur>
          <liensimple xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="https://creativecommons.org/licenses/by-sa/4.0/deed.fr" xlink:actuate="onRequest" xlink:show="replace" xlink:type="simple">
          <objetmedia flot="ligne">
            <image typeimage="forme" xlink:href="http://licensebuttons.net/l/by-sa/4.0/88x31.png" xlink:actuate="onLoad" xlink:show="embed" xlink:type="simple"/>
          </objetmedia>
        </liensimple>
      </droitsauteur>



      </admin>

      <liminaire>
        <grtitre>
          <surtitre>
            <xsl:choose>
              <xsl:when test="(html/body//span[normalize-space(@class) = 'titreDossier'] = 'varia') or (html/body//span[normalize-space(@class) = 'titreDossier'] = 'Varia') or (html/body//span[normalize-space(@class) = 'titreDossier'] = '')">
                <xsl:value-of>Varia</xsl:value-of>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="html/body// span[normalize-space(@class) = 'titreDossier']" />
              </xsl:otherwise>
            </xsl:choose>
          </surtitre>
          <surtitre2>
            <xsl:value-of
              select="
                html/head/meta[normalize-space(@name) = 'DC.type' and
                normalize-space(@class) = 'typeArticle']/@content"
            />
          </surtitre2>
          <titre>
            <xsl:apply-templates select="html/body/div[normalize-space(@id) = 'schema-scholarly-article']/span[normalize-space(@property) = 'name'][1]"/>
          </titre>
          <xsl:if test="html/head/meta[normalize-space(@name) = 'DC.title.Subtitle']">
            <sstitre>
            <xsl:apply-templates select="html/body/div[normalize-space(@id) = 'schema-scholarly-article']/span[normalize-space(@property) = 'name'][2]"/>
            </sstitre>
          </xsl:if>
        </grtitre>

        <grauteur>
          <xsl:for-each select="html/body//div[normalize-space(@class) = 'foaf-author']">
            <auteur>
              <xsl:if
                test="html/body/div[normalize-space(@class) = 'indexations-foaf']//div[normalize-space(@class) = 'foaf-author']//span[normalize-space(@property) = 'gender'] = 'male'">
                <xsl:attribute name="sexe">
                  <xsl:value-of>masculin</xsl:value-of>
                </xsl:attribute>
              </xsl:if>
              <xsl:if
                test="html/body/div[normalize-space(@class) = 'indexations-foaf']//div[normalize-space(@class) = 'foaf-author']//span[normalize-space(@property) = 'gender'] = 'female'">
                <xsl:attribute name="sexe">
                  <xsl:value-of>feminin</xsl:value-of>
                </xsl:attribute>
              </xsl:if>
              <nompers>
                <prenom>
                  <xsl:apply-templates select="span[normalize-space(@property) = 'firstName']"/>
                </prenom>
                <nomfamille>
                  <xsl:apply-templates select="span[normalize-space(@property) = 'familyName']"/>
                </nomfamille>
              </nompers>
            </auteur>
          </xsl:for-each>
        </grauteur>

        <xsl:apply-templates select="/html/body/article/p[(child::span[normalize-space(@class) = 'credits'])]"/>
        <xsl:apply-templates select="/html/body/article/p[(child::span[normalize-space(@class) = 'notice'])]"/>

        <xsl:if test="html/body//div[normalize-space(@class) = 'resume' and normalize-space(@lang) = 'fr']">
          <resume lang="fr">
            <alinea>
              <xsl:apply-templates select="html/body//div[normalize-space(@class) = 'resume' and normalize-space(@lang) = 'fr']"/>
            </alinea>
          </resume>
        </xsl:if>

        <xsl:if test="html/body//div[normalize-space(@class) = 'resume' and normalize-space(@lang) = 'en']">
          <resume lang="en">
            <alinea>
              <xsl:apply-templates select="html/body//div[normalize-space(@class) = 'resume' and normalize-space(@lang) = 'en']"/>
            </alinea>
          </resume>
        </xsl:if>

        <xsl:if test="html/body//div[normalize-space(@class) = 'resume' and normalize-space(@lang) = 'it']">
          <resume lang="it">
            <alinea>
              <xsl:apply-templates select="html/body//div[normalize-space(@class) = 'resume' and normalize-space(@lang) = 'it']"/>
            </alinea>
          </resume>
        </xsl:if>

        <xsl:if test="html/body//div[normalize-space(@class) = 'authorKeywords_fr']">
          <xsl:variable name="autkey"
            select="normalize-space(
              html/body//div[normalize-space(@class) = 'authorKeywords_fr']/span[normalize-space(@property) = 'subject']/string())"/>
          <xsl:variable name="autkeypropre">
            <xsl:choose>
              <xsl:when test="substring($autkey, string-length($autkey)) = '.'">
                <xsl:value-of select="substring($autkey, 1, string-length($autkey)-1)"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="$autkey"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:variable>
          <grmotcle lang="fr">
            <xsl:for-each
              select="tokenize($autkeypropre, ', ')">
              <motcle>
                <xsl:value-of select="."/>
              </motcle>
            </xsl:for-each>
          </grmotcle>
        </xsl:if>


        <xsl:if test="html/body//div[normalize-space(@class) = 'authorKeywords_en']">
          <xsl:variable name="autkey"
            select="normalize-space(
            html/body//div[normalize-space(@class) = 'authorKeywords_en']/span[normalize-space(@property) = 'subject']/string())"/>
          <xsl:variable name="autkeypropre">
            <xsl:choose>
              <xsl:when test="substring($autkey, string-length($autkey)) = '.'">
                <xsl:value-of select="substring($autkey, 1, string-length($autkey)-1)"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="$autkey"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:variable>
          <grmotcle lang="en">
            <xsl:for-each
              select="tokenize($autkeypropre, ', ')">
              <motcle>
                <xsl:value-of select="."/>
              </motcle>
            </xsl:for-each>
          </grmotcle>
        </xsl:if>

        <xsl:if test="html/body//div[normalize-space(@class) = 'authorKeywords_it']">
          <xsl:variable name="autkey"
            select="normalize-space(
            html/body//div[normalize-space(@class) = 'authorKeywords_it']/span[normalize-space(@property) = 'subject']/string())"/>
          <xsl:variable name="autkeypropre">
            <xsl:choose>
              <xsl:when test="substring($autkey, string-length($autkey)) = '.'">
                <xsl:value-of select="substring($autkey, 1, string-length($autkey)-1)"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="$autkey"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:variable>
          <grmotcle lang="it">
            <xsl:for-each
              select="tokenize($autkeypropre, ', ')">
              <motcle>
                <xsl:value-of select="."/>
              </motcle>
            </xsl:for-each>
          </grmotcle>
        </xsl:if>

        <xsl:apply-templates select="html/head/meta[not(normalize-space(@name) = 'DC.subject')]"
          mode="liminaire"/>

      </liminaire>

      <xsl:apply-templates select=".//article"/>

    </article>
  </xsl:template>

  <xsl:template match="meta" mode="liminaire"/>


  <xsl:template match="article">
    <corps>
      <xsl:apply-templates select="p[child::span[normalize-space(@class) = 'dedicace']]"/>
      <xsl:variable name="premEnf" select="*[1][not(self::section)]"/>
      <xsl:if test="$premEnf">
        <section1>
        <xsl:for-each select="child::*[parent::article and not(self::section)]">
          <!-- car les p/span de classe notice ou credits sont placés en liminaire -->
          <xsl:apply-templates select="self::*[not(child::span[normalize-space(@class) = 'notice']) and not(child::span[normalize-space(@class) = 'credits']) and not(child::span[normalize-space(@class) = 'dedicace'])]"/>
        </xsl:for-each>
        </section1>
      </xsl:if>

      <xsl:apply-templates select="section[not(child::div[normalize-space(@class) = 'references']) and not(normalize-space(@class) = 'footnotes')]"/>

    </corps>
    <xsl:if
      test="section[(child::div[normalize-space(@class) = 'references']) or (normalize-space(@class) = 'footnotes')]">
      <partiesann>
        <xsl:attribute name="lang">
          <xsl:value-of select="//meta[normalize-space(@name) = 'DC.language']/@content"/>
        </xsl:attribute>
        <xsl:apply-templates select="section[child::div[normalize-space(@class) = 'references']]"/>
        <xsl:apply-templates select="section[normalize-space(@class) = 'footnotes']"/>
      </partiesann>
    </xsl:if>
  </xsl:template>


  <xsl:template match="section[normalize-space(@class) = 'level2']">
    <section1>
      <xsl:apply-templates/>
    </section1>
  </xsl:template>

<xsl:template match="div[normalize-space(@id) = 'schema-scholarly-article']/span[normalize-space(@property) = 'name']">
	<xsl:apply-templates/>
</xsl:template>

  <xsl:template match="section[normalize-space(@class) = 'level3']">
    <section2>
      <xsl:apply-templates/>
    </section2>
  </xsl:template>

  <xsl:template match="section[normalize-space(@class) = 'level4']">
    <section3>
      <xsl:apply-templates/>
    </section3>
  </xsl:template>

  <xsl:template match="section[normalize-space(@class) = 'level5']">
    <section4>
      <xsl:apply-templates/>
    </section4>
  </xsl:template>

<xsl:template match="h2">
  <titre>
    <xsl:apply-templates/>
  </titre>
</xsl:template>

<xsl:template match="h3">
  <titre>
    <xsl:apply-templates/>
  </titre>
</xsl:template>

<xsl:template match="h4">
  <titre>
    <xsl:apply-templates/>
  </titre>
</xsl:template>

<xsl:template match="h5">
  <titre>
    <xsl:apply-templates/>
  </titre>
</xsl:template>

<xsl:template match="html/body//div[normalize-space(@class) = 'resume']">
	<xsl:apply-templates/>
</xsl:template>



  <xsl:template match="p[not(ancestor::div[normalize-space(@class) = 'resume']) and not(ancestor::div[normalize-space(@class) = 'references']) and not(parent::blockquote) and not(parent::li) and not(child::span[normalize-space(@class) = 'credits']) and not(child::span[normalize-space(@class) = 'notice']) and not(child::span[normalize-space(@class) = 'dedicace'])]">
    <xsl:choose>
      <xsl:when test="child::span[normalize-space(@class) = 'epigraphe']">
        <epigraphe>
          <alinea>
            <xsl:apply-templates/>
          </alinea>
        </epigraphe>
      </xsl:when>
      <xsl:otherwise>
        <para>
          <alinea>
            <xsl:apply-templates/>
          </alinea>
        </para>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="p[child::span[normalize-space(@class) = 'credits']]">
    <notegen typenoteg="edito">
      <alinea>
        <xsl:apply-templates/>
      </alinea>
    </notegen>
  </xsl:template>

  <xsl:template match="p[child::span[normalize-space(@class) = 'notice']]">
    <notegen typenoteg="edito">
      <alinea>
        <xsl:apply-templates/>
      </alinea>
    </notegen>
  </xsl:template>


  <xsl:template match="p[child::span[normalize-space(@class) = 'dedicace']]">
    <dedicace>
      <alinea><xsl:apply-templates/></alinea>
    </dedicace>
  </xsl:template>

  <xsl:template match="p[ancestor::div[normalize-space(@class) = 'references']]">
    <xsl:apply-templates select="node()"/>
  </xsl:template>

<xsl:template match="p[ancestor::div[normalize-space(@class) = 'resume']]">
	<xsl:apply-templates select="node()"/>
</xsl:template>


  <xsl:template match="//figure">
    <xsl:if test="//figure">
    <figure>
      <xsl:if test="descendant::figcaption[not(starts-with(., '&NonBreakingSpace;'))]">
        <legende>
          <xsl:attribute name="lang">
            <xsl:value-of select="//meta[normalize-space(@name) = 'DC.language']/@content"/>
          </xsl:attribute>
          <alinea>
            <xsl:apply-templates select="figcaption/node()"/>
          </alinea>
        </legende>
      </xsl:if>
      <xsl:if test="descendant::img">
        <objetmedia flot="bloc">
          <xsl:for-each select="descendant::img">
            <image>
              <xsl:attribute name="id">
                <xsl:value-of
                  select="normalize-space(substring-after(@src, 'media/'))"
                />
              </xsl:attribute>
              <xsl:attribute name="typeimage">
                <xsl:value-of>figure</xsl:value-of>
              </xsl:attribute>
              <xsl:attribute name="xlink:type">
                <xsl:value-of>simple</xsl:value-of>
              </xsl:attribute>
            </image>
          </xsl:for-each>
        </objetmedia>
      </xsl:if>
      <xsl:if test="/p[normalize-space(@class) = 'source']">
        <source>
          <xsl:apply-templates select="/p[normalize-space(@class) = 'source']/node()"/>
        </source>
      </xsl:if>
    </figure>
    </xsl:if>
  </xsl:template>

  <xsl:template match="ol">
    <listeord numeration="decimal">
      <xsl:apply-templates/>
    </listeord>
  </xsl:template>

  <xsl:template match="ul">
    <listenonord signe="disque">
      <xsl:apply-templates/>
    </listenonord>
  </xsl:template>

  <xsl:template
    match="article//p/ul/li[not(child::p)] | article//ul/li[not(child::p)] | article//ol/li[not(child::p)] | article//p/ol/li[not(child::p)]">
    <elemliste>
      <alinea>
        <xsl:apply-templates/>
      </alinea>
    </elemliste>
  </xsl:template>

  <xsl:template
    match="article//p/ul/li[child::p] | article//ul/li[child::p] | article//ol/li[child::p] | article//p/ol/li[child::p]">
    <elemliste>
        <xsl:apply-templates/>
    </elemliste>
  </xsl:template>

  <xsl:template match="li//p">
    <alinea>
      <xsl:apply-templates/>
    </alinea>
  </xsl:template>

  <xsl:template match="blockquote//p">
    <alinea>
      <xsl:apply-templates select="child::node()[not(self::span[@class='citation'])]"/>
    </alinea>
    <xsl:apply-templates select="span[@class='citation']"/>
  </xsl:template>

  <xsl:template match="blockquote">
    <bloccitation>
      <xsl:apply-templates/>
    </bloccitation>
  </xsl:template>

  <!-- sortir la source de l'alinea de la blockquote -->
  <xsl:template match="blockquote/p/span[@class='citation']">
    <source>
      <xsl:apply-templates/>
    </source>
  </xsl:template>

  <xsl:template match="em">
    <marquage typemarq="italique">
      <xsl:apply-templates/>
    </marquage>
  </xsl:template>

  <xsl:template match="sup[../@class='footnote-ref']">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="sup">
    <exposant>
      <xsl:apply-templates/>
    </exposant>
  </xsl:template>

  <xsl:template match="sub">
    <indice>
      <xsl:apply-templates/>
    </indice>
  </xsl:template>

  <xsl:template match="b">
    <marquage typemarq="gras">
      <xsl:apply-templates/>
    </marquage>
  </xsl:template>

  <xsl:template match="strong">
    <marquage typemarq="gras">
      <xsl:apply-templates/>
    </marquage>
  </xsl:template>

  <xsl:template match="span">
    <xsl:apply-templates/>
  </xsl:template>


  <!-- TODO br > alinea  -->
  <xsl:template match="br">
    <xsl:value-of disable-output-escaping="yes">&lt;/alinea&gt;&lt;alinea&gt;</xsl:value-of>
  </xsl:template>

  <xsl:template match="hr">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="center[normalize-space(node())='⁂']">
    <para>
      <alinea>
        <xsl:apply-templates/>
      </alinea>
    </para>
  </xsl:template>

  <xsl:template match="a">
    <xsl:choose>
      <xsl:when test="./@href[starts-with(., '#ref-')]">
        <xsl:apply-templates/>
      </xsl:when>
      <xsl:otherwise>
        <liensimple xlink:type="simple" xlink:href="{@href}">
          <xsl:apply-templates/>
        </liensimple>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="*">
    <xsl:copy-of select="."/>
  </xsl:template>

  <xsl:template name="compte">
    <xsl:param name="de"/>
    <xsl:param name="jusque"/>
    <xsl:choose>
      <xsl:when test="$de">
        <xsl:variable name="decompte">
          <xsl:call-template name="compte">
            <xsl:with-param name="de"
              select="
                $de/following-sibling::*[1][not(contains($jusque,
                concat(' ', name(), ' ')))]"/>
            <xsl:with-param name="jusque" select="$jusque"/>
          </xsl:call-template>
        </xsl:variable>
        <xsl:value-of select="1 + $decompte"/>
      </xsl:when>
      <xsl:otherwise>0</xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="html/body//section[normalize-space(@class) = 'footnotes']">
    <grnote>
      <xsl:apply-templates select="ol"/>
    </grnote>
  </xsl:template>

  <xsl:template match="html/body//section[normalize-space(@class) = 'footnotes']/ol">
    <xsl:for-each select="li">
      <note>
        <xsl:attribute name="id">
          <xsl:value-of select="concat('sdfootnote', substring-after(@id, 'fn'), 'sym')"/>
        </xsl:attribute>
        <no>
          <xsl:value-of select="position()"/>
        </no>
        <xsl:apply-templates/>
      </note>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="a[normalize-space(@class) = 'footnote-ref']">
    <renvoi typeref="note">
      <xsl:attribute name="idref">
        <xsl:value-of select="concat('sdfootnote', substring-after(@id, 'fnref'), 'sym')"/>
      </xsl:attribute>
      <xsl:apply-templates/>
    </renvoi>
  </xsl:template>

  <xsl:template
    match="
      html/body//section[normalize-space(@class) =
      'footnotes']//p/a[not(following-sibling::* | following-sibling::text()[normalize-space()])]"/>

  <xsl:template match="section[child::div[normalize-space(@class) = 'references']]">
    <xsl:variable name="titlebib" select="child::h2"/>
    <grbiblio>
      <biblio>
        <titre><xsl:value-of select="$titlebib"/></titre>
        <xsl:for-each select="child::div[normalize-space(@class) = 'references']/div">
          <refbiblio>
            <xsl:apply-templates select="node()"/>
          </refbiblio>
        </xsl:for-each>
      </biblio>
    </grbiblio>

  </xsl:template>


</xsl:stylesheet>
