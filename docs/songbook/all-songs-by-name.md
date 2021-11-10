---
layout: page
title: Songbook
subtitle: 我们唱过的所有歌曲都在这里了
permalink: /all-songs-by-name/
---

{% assign songs = site.data.songs %}
{% for song in songs -%}
- {{ song.name }} - {{ song.key }} 
{% endfor %}
