# Aparat_PlayList_Downloader
- this is simple script for download aparat playlist 
- this app work tow mode : online and offline mode
- offline mode just for get playlist links work
  and for generate download link you need connect to internet  
  
  
 ### online usage example:
 if your playlist address is : 
<pre>https://www.aparat.com/playlist/251724</pre>
 use :
<pre><code> python app.py -code="251724" -out="d:\aparat"</code></pre>
 ### offline usage example:
 <pre><code> python app.py -code="251724" file="play.html" -online="n"  -out="d:\aparat"</code></pre>   
 