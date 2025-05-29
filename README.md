# AI_werewolf
我是國立高雄科技大學資管所碩士一甲的龔玖恩（F113118131），這是我的生成式AI的期末專案，主要内容是透過以Gemini API為大腦的AI狼人殺游戲。

## Register Gemini Api Key
Website: https://aistudio.google.com/app/apikey
**open cmd**
<pre><code>setx GEMINI_API_KEY *your_api_key_here* </code></pre>
**check the variable**
<pre><code>echo %GEMINI_API_KEY%</code></pre>

## How To Install
**create enviroment**
<pre><code>conda create --name werewolf python=3.10.0</code></pre>
<pre><code>conda activate werewolf</code></pre>
**clone project**
<pre><code>git clone https://github.com/gabrielk1234/AI_werewolf.git</code></pre>
<pre><code>cd AI_werewolf/</code></pre>
**install requirement**
<pre><code>pip install -r .\requirement.txt</code></pre>
<pre><code>cd werewolfgame</code></pre>
**start server**
<pre><code>python manage.py runserver</code></pre>
