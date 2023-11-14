<xsl:stylesheet version="2.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fn="http://www.w3.org/2005/xpath-functions"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                xpath-default-namespace="http://www.erudit.org/xsd/article">

  <!-- récupère l'id de l'article traité -->
  <xsl:variable name="idArticle" select="substring-before(substring-after(base-uri(),'Edition/./SP'),'/')" />

  <!-- By default, copy elements and attributes unchanged -->
  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>


  <!-- modifier article/@idref avec le sommaire -->
  <xsl:template match="/article/@idref">
    <xsl:attribute name="idref">
      <xsl:value-of select="document('/home/nicolas/gitlab/SP-articles/Edition/sommaire2018.xml')/*:sommaire/*:article[@id=$idArticle]/@dossier"/>
    </xsl:attribute>
  </xsl:template>

  <!-- modifier ordseq avec le sommaire -->
  <!-- <xsl:template match="/article/@ordseq">
    <xsl:attribute name="ordseq">
      <xsl:value-of select="document('/home/nicolas/gitlab/SP-articles/Edition/sommaire2018.xml')/*:sommaire/*:article[@id=$idArticle]/@ordseq"/>
    </xsl:attribute>
  </xsl:template> -->

  <!-- modifier un attribut en fonction d'un test -->
  <!-- <xsl:template match="/article/admin/droitsauteur[2]/liensimple/@xlink:href">
      <xsl:if test="contains(/article/admin/droitsauteur[1],'NonCommercial')">
        <xsl:attribute name="href" namespace="http://www.w3.org/1999/xlink">https://creativecommons.org/licenses/by-nc-sa/4.0/deed.fr</xsl:attribute>
      </xsl:if>
      <xsl:if test="not(contains(/article/admin/droitsauteur[1],'NonCommercial'))">
        <xsl:attribute name="href" namespace="http://www.w3.org/1999/xlink">https://creativecommons.org/licenses/by-sa/4.0/deed.fr</xsl:attribute>
      </xsl:if>
  </xsl:template>

  <xsl:template match="/article/admin/droitsauteur[2]/liensimple/objetmedia/image/@xlink:href">
      <xsl:if test="contains(/article/admin/droitsauteur[1],'NonCommercial')">
        <xsl:attribute name="href" namespace="http://www.w3.org/1999/xlink">http://licensebuttons.net/l/by-nc-sa/4.0/88x31.png</xsl:attribute>
      </xsl:if>
      <xsl:if test="not(contains(/article/admin/droitsauteur[1],'NonCommercial'))">
        <xsl:attribute name="href" namespace="http://www.w3.org/1999/xlink">http://licensebuttons.net/l/by-sa/4.0/88x31.png</xsl:attribute>
      </xsl:if>
  </xsl:template> -->
  <!-- FIN modifier un attribut en fonction d'un test -->

</xsl:stylesheet>
