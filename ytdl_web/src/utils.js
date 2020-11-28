const millisecToHumanReadable = (millisec) => {
    var seconds = (millisec / 1000).toFixed(0);
    var minutes = Math.floor(seconds / 60);
    var hours = "";
    if (minutes > 59) {
        hours = Math.floor(minutes / 60);
        hours = (hours >= 10) ? hours : "0" + hours;
        minutes = minutes - (hours * 60);
        minutes = (minutes >= 10) ? minutes : "0" + minutes;
    }

    seconds = Math.floor(seconds % 60);
    seconds = (seconds >= 10) ? seconds : "0" + seconds;
    if (hours != "") {
        return hours + ":" + minutes + ":" + seconds;
    }
    return minutes + ":" + seconds;
};


const bytesToHumanReadableFileSize = (bytes)  => {
    if (bytes < 1024) return bytes + ' B';
    let i = Math.floor(Math.log(bytes) / Math.log(1024));
    let num = (bytes / Math.pow(1024, i));
    let round = Math.round(num);
    num = round < 10 ? num.toFixed(2) : round < 100 ? num.toFixed(1) : round;
    return `${num} ${'KMGTPEZY'[i-1]}B`
  }

export {millisecToHumanReadable, bytesToHumanReadableFileSize};