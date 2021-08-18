
const project-div = document.querySelector(".project-div"); //hero
const wc-image = document.querySelector(".wc-image");       //hero image
const watering-can = document.querySelector(".watering-can");   //headline
const slider = document.querySelector(".slider");   //slider

const tl = new TimelineMax();

tl.add("step0")
    .fromTo(project-div, 4, {height: 0%}, {height: 80%, ease: Power2.easeInOut})
    .fromTo(project-div, 6, {width: 100%}, {width: 80%, ease: Power2.easeInOut})
    .fromTo(slider, 5, {x: "-100%"}, {x: "0%", ease: Power2.easeInOut}, -6);


