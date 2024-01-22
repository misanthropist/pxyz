var timestamps = $(".timestamp"),
    offset = (new Date()).getTimezoneOffset(),
    count = timestamps.length;

for (var i = 0; i < count; i++) {
    var ymdhms = timestamps[i].textContent.split(' '),
        ymd = ymdhms[0],
        hms = ymdhms[1].split(':'),
        h = parseInt(hms[0])-offset/60,
        m = hms[1],
        s = hms[2];
    timestamps[i].textContent = ymd+' '+h.toString()+':'+m.toString()+':'+s.toString();
}


