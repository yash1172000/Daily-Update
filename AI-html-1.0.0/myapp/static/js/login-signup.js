document.addEventListener('DOMContentLoaded', (event) => {
    // Get the video and button elements
    const video = document.getElementById('videoPlayer');
    const playButton = document.getElementById('playButton');
    const pauseButton = document.getElementById('pauseButton');
    // Play video when the play button is clicked
    playButton.addEventListener('click', function () {
        video.play();
        playButton.style.display = 'none';
        pauseButton.style.display = 'block';
    });
    // Pause video when the pause button is clicked
    pauseButton.addEventListener('click', function () {
        video.pause();
        pauseButton.style.display = 'none';
        playButton.style.display = 'block';
    });
});

document.addEventListener('DOMContentLoaded', (event) => {
    // Get the video and button elements
    const video = document.getElementById('videoPlayer');
    const playButton = document.getElementById('playButton');
    const pauseButton = document.getElementById('pauseButton');

    // Play video when the play button is clicked
    playButton.addEventListener('click', function () {
        video.play();
        playButton.style.display = 'none';
        pauseButton.style.display = 'block';
    });

    // Pause video when the pause button is clicked
    pauseButton.addEventListener('click', function () {
        video.pause();
        pauseButton.style.display = 'none';
        playButton.style.display = 'block';
    });
});
