$(document).ready(function () {
  const $sliderTrack = $('.slider-track');
  const scrollAmount = 400;

  $('.slider-wave.left').click(function () {
    $sliderTrack.animate({
      scrollLeft: $sliderTrack.scrollLeft() - scrollAmount
    }, 300);
  });

  $('.slider-wave.right').click(function () {
    $sliderTrack.animate({
      scrollLeft: $sliderTrack.scrollLeft() + scrollAmount
    }, 300);
  });
});