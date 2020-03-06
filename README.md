## Aparat_PlayList_Downloader
- this is simple script for download aparat playlist 

 ###  usage example:
 if your playlist address is : 
 
<pre>https://www.aparat.com/v/VgFSr?playlist=110553</pre>
 **use :**
 <pre><code> python App.py -url=https://www.aparat.com/v/VgFSr?playlist=110553</code></pre>

**or use :**
<pre><code> python App.py -url=https://www.aparat.com/v/VgFSr?playlist=110553 -out="d:\media"</code></pre>

* for generate exe file use :
<pre><code>  pyinstaller --onefile --ico=aparat.ico --name=aparat.exe App.py </code></pre>

 **and then use in cmd :**
<pre><code>  aparat.exe -url=https://www.aparat.com/v/VgFSr?playlist=110553 -out="d:\media"</code></pre>