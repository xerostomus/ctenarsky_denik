<?xml version = "1.0" encoding = "UTF-8"?>
<xsl:stylesheet version = "1.0" xmlns:xsl = "http://www.w3.org/1999/XSL/Transform">   
<xsl:strip-space elements="*"/>

<xsl:template  match = "/"> 
<!-- Napred vyhleda tento korenovy adresar -->
  
   <html> 
    <style>
body	{ margin-left:3%; margin-right:3%; font-size: 130%; line-height: 140% }
pre		{font-size:110%; text-align: left;  margin-left: 100; margin-top:0; font-family: "Mono", sans-serif;  }
p		{text-align: justify;  margin-bottom: 5; margin-top:0; }
li		{text-align: justify;  margin-bottom: 5; margin-top:0; line-height: 200% }
.vo 	{text-indent: 1cm; text-align: justify }
.to		{text-indent: 1cm; text-align: justify; font-weight: bold }
.vvp	{text-indent: 0; text-align: Right; }
.tvp	{text-indent: 0; text-align: Right; font-weight: bold }
.vvl	{text-indent: 0; text-align: Left; }
.tvl	{text-indent: 0;text-align: Left; font-weight: bold }
.vs	{text-indent: 0;  text-align: center; }
.ts	{text-indent: 0; text-align: center;  font-weight: bold }
.t 	{text-indent: 0; font-size: 16; font-weight: bold; font-family:  sans-serif; }
.mt 	{color:darkgreen; text-indent: 20; margin-bottom:0; font-family:  sans-serif; font-size: 130%; font-weight: bold; }
.se	{text-indent: 0%; padding-left: 1%; margin-left: 15; text-align: justify;margin-bottom: 5; margin-top:0;}
.r1	{text-indent: 0; margin-bottom: 0; margin-top:0;line-height: 100% }
.r12  	{text-indent:  2cm; margin-bottom: 0; margin-top:0;line-height: 100% }
.l 	{margin-bottom: 0cm; border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: none; border-right: none;font-family:  sans-serif; ; line-height: 150% }
.pr 	{margin-left: 0.52cm; text-indent: 0cm; margin-bottom: 0cm; font-family:  sans-serif; line-height: 150% }
table, th, td, tr {  border: 1px solid black;  border-collapse: collapse; valign: center}
h1   { font-size: 24pt; font-weight: bold; text-align:center; font-family:  sans-serif; }
h2   { color:darkblue; text-align: left;  font-weight: bold; font-family:  sans-serif; }
h3   { font-size: 14pt; font-weight: bold; margin-bottom:0; font-family:  sans-serif; }
h4   { font-size: 24pt; font-weight: bold; text-align:center;font-family:  sans-serif;  }
h5   { text-align: center; font-size: 16pt; font-weight: bold;font-family:  sans-serif;  }
h6   { font-size: 14pt; font-weight: bold; margin-bottom:0;font-family:  sans-serif;  }
</style>
<body>

<h1>Čtenářský deník</h1> 
<p class="ts">PhDr. Mgr. Jeroným Klimeš, Ph.D. 2022-05-15</p>
<p class="vo">Konečně! Konečně jsem si pořídil čtenářský deník pro trochu kultivované zapisování poznámek z knih. Doposud jsem to měl naprosto chaoticky v různých textových souborech. Zkrátka na počítači se musí všechno dělat jinak než u tištěných knih. Tak jsem si na to napsal krátký script v Pythonu (Linux) a tento XSL soubor, který docela hezky zobrazuje XML soubor, detaily na konci stránky. Vše je pod licencí GNU-GPL, takže pokud se Vám tento projekt líbí, můžete si ho lehce vytvořit též.</p>	

<hr />
<!-- 		Tady vytvor obsah podle templates -->
	<xsl:call-template name="obsah" />
	<xsl:apply-templates/>
	<!-- 		Sem načti zbyvajici urovne, tzn. knihy a vys -->
<hr />
<p class="mt">Poznámka</p>
<p class="vo"><a href="ctenarsky_denik.xml">XML soubor</a> obsahuje strukturované informace o knihách. V druhém <a href="ctenarsky_denik.xsl">XSL souboru</a> je návod, jak tyto informace úhledně zobrazit. Když zavoláte v prohlížeči soubor XML, server (www.mysteria.cz) vám ale vrátí soubor HTML, který byl vytvořen sloučením XML a XSL souboru. To je ten, který právě čtete.</p>
<p class="vo">Na lokálním počítači ale tuto konverzi dělám <a href="ctenarsky_denik_sh.txt">příkazem</a>:</p>
<pre>
xsltproc  ctenarsky_denik.xsl ctenarsky_denik.xml >  /dev/shm/ctenarsky_denik.htm
firefox  /dev/shm/ctenarsky_denik.htm &amp;
xdotool windowactivate $(xdotool search "firefox" | tail -n 1) # to je navic
</pre>
<p class="vo"><a href="ctenarsky_denik.py">Čtenářský deník - Python skript</a> pro generování XML v Linuxu. Pro Windows lze lehce upravit. Pomocí něho může zádávat nové knihy a citace. Program ve stavu zrodu, mnoho funkcí chybí, popř. nefunguje správně. Použití na vlastní nebezpečí. Více v nápovědě:</p> 
<pre>
ctenarsky_denik.py --napoveda
</pre>

</body> 
</html> 
</xsl:template>  

<xsl:template match="/knihy/kniha/autor" mode="toc" name="obsah">
<!-- 	OBSAH nešahat -->
	<xsl:for-each select="/knihy/kniha"> 
		<xsl:sort select="autor"/>
		<li class="se">
		<a>
			<xsl:attribute name="href">
				<xsl:value-of select="concat('#id', id)" />
			</xsl:attribute>
			<xsl:value-of select = "id"/>
		</a>  
		. <xsl:value-of select = "autor"/>: <xsl:value-of select = "nazev"/>
		</li>
	</xsl:for-each> 
</xsl:template>

<xsl:template match="kniha" >
	<hr />
	<h2>
		<a>
			<xsl:attribute name="name">
				<xsl:value-of select="concat('id', id)" />
			</xsl:attribute>
		<xsl:value-of select = "id"/>.
		<xsl:value-of select = "autor"/>:
		<xsl:value-of select = "nazev"/>
		</a>
	</h2>
   	<xsl:apply-templates select="poznamka"/> 
<!--    	Toto apply určuje pořadí zobrazení -->
   	<xsl:apply-templates select="url"/> 
   	<xsl:apply-templates select="citace"/> 
	<xsl:for-each select="citat"> 
<!-- 		Tady apply-templates nefunguje-->
		<xsl:call-template name="citat" /> 
	</xsl:for-each>
</xsl:template>  

<xsl:template match="kniha/id" name="id" >
	<p>ID skrečuj</p>
</xsl:template>  

<xsl:template match="kniha/autor" name="autor">
	<p>autora skrečuj</p>
</xsl:template> 

<xsl:template match="kniha/nazev" name="nazev" >
	<p>nazev skrečuj</p>
</xsl:template>

<xsl:template match="citat" name="citat">
   	<xsl:apply-templates select="nadpis"/> 
   	<xsl:apply-templates select="text"/> 
   	<xsl:apply-templates select="komentar"/> 
   	<xsl:apply-templates select="strana"/> 
</xsl:template>

<xsl:template match="nadpis" name="nadpis" >
	<xsl:if test=". != '' ">
	<p class="mt"><xsl:apply-templates/></p>
	</xsl:if>
</xsl:template>  

<xsl:template match="komentar" name="komentar" >
	<xsl:if test=". != '' ">
	<p class="se"><b>Komentář: </b><xsl:apply-templates/></p>
	</xsl:if>
</xsl:template>  

<xsl:template match="text" name="text" >
	    <xsl:call-template name="p" />
</xsl:template>  

<xsl:template match="strana" name="strana" >
	<xsl:if test=". != '' ">
		<p class="vvp">Str. <xsl:value-of select="." /></p>
	</xsl:if>
</xsl:template>  

<xsl:template match="citace"  name="citace">
	<xsl:if test=". != '' ">
	<p class="se"><b>Citace: </b><xsl:value-of select = "."/></p>
	</xsl:if>
</xsl:template>  

<xsl:template match="kniha/url" name="url">
	<xsl:if test=". != '' ">
	<p class="se"><b>URL: </b>  
		<a>
			<xsl:attribute name="href">
				<xsl:value-of select="." />
			</xsl:attribute>
			<xsl:attribute name="target">
				<xsl:value-of select="_blank" />
			</xsl:attribute>
			<xsl:value-of select="." />
		</a>  
	</p>
	</xsl:if>
</xsl:template>  

<xsl:template match="kniha/poznamka" name="poznamka">
	<xsl:if test=". != '' ">
	<p class="se"><b>Poznámka: </b> <xsl:value-of select = "."/></p>
	</xsl:if>
</xsl:template>  


<xsl:template match="p" name="p">
		<p class="vo"><xsl:apply-templates/></p>
</xsl:template>

<xsl:template match="datum" >
<!-- 	<xsl:apply-templates/> -->
<!--	datum provizorne skrečujem
<xsl:if test=". != '' ">
		<p class="vvp">
		<xsl:apply-templates/>
		</p>
	</xsl:if>
-->
</xsl:template>

<xsl:template match="b" >
	<b><xsl:value-of select="." /></b>
</xsl:template>

<xsl:template match="pre" >
	<pre><xsl:apply-templates/></pre>
</xsl:template>

<xsl:template match="br" >
	<br />
</xsl:template>

<xsl:template match="u" >
	<u><xsl:value-of select="." /></u>
</xsl:template>

<xsl:template match="mark" name="mark">
	<mark><xsl:value-of select="." /></mark>
</xsl:template>

<xsl:template match="i" name="i">
		<i><xsl:value-of select="." /></i>
</xsl:template>

</xsl:stylesheet>
