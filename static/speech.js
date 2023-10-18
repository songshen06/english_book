document.addEventListener("DOMContentLoaded", function() {
    // 在文档加载完毕后，将事件侦听器绑定到 "Pronounce" 按钮上。
    const pronounceButton = document.getElementById("pronounce-button");
    if (pronounceButton) {
        pronounceButton.addEventListener("click", speakInput);
    }
});

function speakInput() {
    // 获取用户在文本框中输入的值
    const inputValue = document.querySelector("[name='word_input']").value;
    if (inputValue) {
        speak(inputValue);
    } else {
        alert("Please input a word to pronounce.");
    }
}

function speak(text) {
    // 使用 Web Speech API 进行发音
    const synthesis = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    synthesis.speak(utterance);
}
document.addEventListener("DOMContentLoaded", function() {
    // ... 原始代码 ...
    
    // 绑定录音按钮的事件侦听器
    const recordButton = document.getElementById("record-button");
    if (recordButton) {
        recordButton.addEventListener("click", recordPronunciation);
    }
    
    // 绑定跳过按钮的事件侦听器
    const skipButton = document.getElementById("skip-button");
    if (skipButton) {
        skipButton.addEventListener("click", skipWord);
    }
});

function recordPronunciation() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US'; // 设定英语为目标语言
    recognition.onresult = function(event) {
        const userPronunciation = event.results[0][0].transcript;
        comparePronunciation(userPronunciation);
    };
    recognition.start();
}

function comparePronunciation(userPronunciation) {
    const correctPronunciation = document.querySelector("[name='word_input']").value;
    if (userPronunciation.toLowerCase() !== correctPronunciation.toLowerCase()) {
        alert("Incorrect pronunciation. Try again!");
    } else {
        alert("Correct pronunciation!");
        // 你可以在这里添加代码，例如自动加载下一个单词等等
    }
}

function skipWord() {
    alert("Skipped!");
    // 你可以在这里添加代码，例如加载下一个单词或其他操作
}