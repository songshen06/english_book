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
