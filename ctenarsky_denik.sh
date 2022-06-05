# 
# 
# adresar=/dev/shm
# soubor=ctenarsky_denik
# echo "xsltproc  $soubor.xsl $soubor.xml >  $adresar/$soubor.htm"
# xsltproc  $soubor.xsl $soubor.xml >  $adresar/$soubor.htm
# echo "firefox  $adresar/$soubor.htm &"
# firefox  $adresar/$soubor.htm &
# xdotool windowactivate $(xdotool search "firefox" | tail -n 1)

adresar=/dev/shm
soubor=ctenarsky_denik
soubor_xsl=a
soubor_xsl=$soubor
echo "xsltproc  $soubor_xsl.xsl $soubor.xml >  $adresar/$soubor.htm"
# xsltproc --verbose $soubor_xsl.xsl $soubor.xml >  $adresar/$soubor.htm
xsltproc $soubor_xsl.xsl $soubor.xml >  $adresar/$soubor.htm
if [ $? -gt 0 ];then exit;fi
echo "firefox  $adresar/$soubor.htm &"
firefox  $adresar/$soubor.htm &
xdotool windowactivate $(xdotool search "firefox" | tail -n 1)

