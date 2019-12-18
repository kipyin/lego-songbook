---
layout: page
title: 所有音乐
permalink: /all-songs/
---

{% assign song_by_name = site.data.songs | sort: "name" %}
| Name | Key | Sheet | 圣诗精选 |
|:---:|:---:|:---:|:---:|
{% for song in song_by_name -%}

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
