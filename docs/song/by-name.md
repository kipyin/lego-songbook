---
layout: page
title: Songbook
subtitle: 我们唱过的所有歌曲都在这里了
permalink: /song/by-name/
---

{% assign songs = site.data.songs %}
{% for song in songs -%}
- [{{ song.name }}]({{ site.baseurl }}/song/{{ song.name }}/) - {{ song.key }} 
{% endfor %}