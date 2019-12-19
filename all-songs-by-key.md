---
layout: page-hidden
title: 所有音乐
permalink: /all-songs-by-key/
---

{% assign songs = site.data.songs_by_key %}
| [Name]({{ site.baseurl }}/all-songs-by-name/) | [Key]({{ site.baseurl }}/all-songs-by-key/) | Sheet | 诗歌本 |
|:---:|:---:|:---:|:---:|
{% for song in songs -%}

{%- capture sheet_link -%}
http://pz2c5nkyy.bkt.clouddn.com/{{ song.key | url_encode}}-{{ song.name | url_encode | replace: "+", "%20" }}-{{ song.sheet_type | url_encode }}.jpg
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

| {{ song.name }} | {{ song.key }} | [{{ song.sheet_type }}]({{ sheet_link }}) | {{ hymn_link }} |
{% endfor %}
