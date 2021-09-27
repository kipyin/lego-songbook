---
layout: page
title: Songbook
subtitle: 我们唱过的所有歌曲都在这里了
permalink: /all-songs-by-name/
---

{% assign songs = site.data.songs %}
| [名称]({{ site.baseurl }}/all-songs-by-name/) | [曲调]({{ site.baseurl }}/all-songs-by-key/) | 歌谱 |
|:---:|:---:|:---:|
{% for song in songs -%}

{%- capture sheet_link -%}
{{ site.sheet_link }}{{ song.name | url_encode | replace: "+", "%20" }}.{{ song.sheet_type | url_encode }}
{%- endcapture -%}

{%- capture hymn_link -%}
    {%- if song.hymn != "--" -%}
        {%- assign hymn = song.hymn | abs -%}
        {%- if hymn < 10 -%}
            {%- assign hymn_number = song.hymn | prepend: "00" -%}
        {%- elsif hymn < 100 -%}
            {%- assign hymn_number = song.hymn | prepend: "0" -%}
        {%- else -%}
            {%- assign hymn_number = song.hymn -%}
        {%- endif -%}

        [{{ song.hymn }}](http://sw.51christ.com/img/{{ song.hymn }}.png) [音频](http://sw.51christ.com/zanmei/{{ hymn_number }}.mp3)
    {%- endif -%}
{%- endcapture -%}

| {{ song.name }} | {{ song.key }} | [{{ song.sheet_type | upcase }}]({{ sheet_link }}) |
{% endfor %}
