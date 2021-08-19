/*
const project = document.querySelector(".project-div");
const watering-can = document.querySelector(".watering-can");
const slider = document.querySelector(".slider");
*/
const wcimage = document.querySelector(".wc-image");
const tl = new TimelineMax();
tl.fromTo(wcimage, 1, {height: "0%"}, {height: "80%"});
/*
    .fromTo(wcimage, 6, {width: "100%"}, {width: "80%", ease: Power2.easeInOut});
    .fromTo(slider, 5, {x: "-100%"}, {x: "0%", ease: Power2.easeInOut}, -6);
*/

