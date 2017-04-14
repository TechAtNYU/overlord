/*
  script expects one arg - JSON object
*/

// var page = require('webpage').create();
// var system = require('system');
// var fs = require('fs');
var request = require('request');

// page.viewportSize = {
//   width: 1024,
//   height: 900
// };

// const contactInfoObj = {
//   firstName: "David",
//   lastName: "Wang",
//   email: "dhw249@stern.nyu.edu",
//   phone: "8608199613",
//   address: "65 East 11th Street, 1A",
//   city: "New York",
//   state: "New York",
//   zip: "10010",
// };

// var submitEventToOrgsync = function(eventObj) {
//   for(var key in eventObj) {
//     if(eventObj.hasOwnProperty(key)) {
//       if(eventObj[key] === undefined || eventObj[key] === null) {
//         // incomplete or invalid data
//         console.log("incomplete or invalid event data... exiting");
//         exit();
//       }
//     }
//   }

//   var uName = system.env['TNYU_ORGSYNC_USERNAME'];
//   var uPass = system.env['TNYU_ORGSYNC_PASSWORD'];
//   var credentials = {"uName": uName, "uPass": uPass};

//   if(uName === undefined || uPass === undefined){
//     console.log("can't authenticate... exiting");
//     exit();
//   }

//   page.open('http://orgsync.com/sso_redirect/new-york-university', function(status){
//     console.log(status + ' on initial auth redirect');
//     if(status === 'success'){
//       page.render('page1.png');
//       page.evaluate(function(credentials){
//         // Add your nyu username and pass here as env variables
//         var uName = credentials["uName"];
//         var uPass = credentials["uPass"];
//         document.getElementById('netid').value = uName;
//         document.getElementById('password').value = uPass;
//         document.getElementById('login').lastElementChild.click();
//       },credentials);
//       var t = setTimeout(function(){
//         two('https://orgsync.com/61895/events/new');
//       }, 6000);
//     }
//   });

//   function confirm() {
//     console.log("logging a confirm message...");
//     page.evaluate(function(eventObj){

//     }, eventObj);
//     page.render('confirm_message.png');
//     setTimeout(function(){
//       exit();
//     }, 4000);
//   }

//   function verifySubmit() {
//     console.log("verifying and submitting...");
//     page.evaluate(function(eventObj){
//       document.getElementsByClassName("button green")[0].click();
//     }, eventObj);
//     page.render('verify.png');
//     setTimeout(function(){
//       confirm();
//     }, 4000);
//   }

//   function ten() {
//     console.log("opening page 10...");
//     page.evaluate(function(eventObj){
//       document.getElementById("responses_652756").value = eventObj.advisorEmail;
//       document.getElementsByClassName("button green")[0].click();
//     }, eventObj);
//     page.render('page10.png');
//     setTimeout(function(){
//       verifySubmit();
//     }, 4000);
//   }

//   function nine() {
//     console.log("opening page 9...");
//     page.evaluate(function(eventObj){
//       document.getElementById("responses_954552_address").value = eventObj.contactInfo.address;
//       document.getElementById("responses_954552_city").value = eventObj.contactInfo.city;
//       document.getElementById("responses_954552_state").value = eventObj.contactInfo.state;
//       document.getElementById("responses_954552_zip").value = eventObj.contactInfo.zip;
//       document.getElementsByClassName("button green")[0].click();
//     }, eventObj);
//     page.render('page9.png');
//     setTimeout(function(){
//       ten();
//     }, 4000);
//   }

//   function eight() {
//     console.log("opening page 8...");
//     page.evaluate(function(eventObj){
//       if(eventObj.areChargingForAddmission){
//         document.getElementById("responses_652739_1072710").click();
//       } else {
//         document.getElementById("responses_652739_1072709").click();
//       }
//       document.getElementById("responses_652741_1072711").click();
//       document.getElementsByClassName("button green")[0].click();
//     }, eventObj);
//     page.render('page8.png');
//     setTimeout(function(){
//       nine();
//     }, 4000);
//   }

//   function seven() {
//     console.log("opening page 7...");
//     page.evaluate(function(eventObj){
//       document.getElementById('responses_652729').getElementsByTagName('select')[0].value = "1072583"; // default of 'Other NYU Building'
//       document.getElementsByClassName("button green")[0].click();
//     }, eventObj);
//     page.render('page7.png');
//     setTimeout(function(){
//       eight();
//     }, 4000);
//   }

//   function six() {
//     console.log("opening page 6...");
//     page.evaluate(function(eventObj){
//       document.getElementById("responses_652727").value = eventObj.eventSpeakers;
//       document.getElementsByClassName("button green")[0].click();
//     }, eventObj);
//     page.render('page6.png');
//     setTimeout(function(){
//       seven();
//     }, 4000);
//   }

//   function five() {
//     console.log("opening page 5...");
//     page.evaluate(function(eventObj){
//       document.getElementById("responses_652724").value = eventObj.coSponsoringClubs;
//       var button = document.getElementsByClassName("button green")[0];
//       button.click();
//     }, eventObj);
//     page.render('page5.png');
//     setTimeout(function(){
//       six();
//     }, 4000);
//   }

//   function four() {
//     console.log("opening page 4...");
//     page.evaluate(function(){
//       // clicking everything to "no" -> check with Brenton
//       document.getElementById("responses_652720_1072546").click();
//       document.getElementById("responses_652721_1072548").click();
//       document.getElementById("responses_652722_1072550").click();
//       document.getElementById("responses_652723_1072552").click();
//       document.getElementsByClassName("button green")[0].click();
//     });
//     page.render('page4.png');
//     setTimeout(function(){
//       five();
//     }, 4000);
//   }

//   function three(){
//     console.log("opening page 3...");
//     page.evaluate(function(){
//       document.getElementById('responses_652719').getElementsByTagName('select')[0].value = "1072545"; // workshop category
//       var checkbox = document.getElementById('responses_742065_1237695');
//       checkbox.click();
//       document.getElementsByClassName('button green')[0].click();
//     });
//     page.render('page3.png');
//     setTimeout(function(){
//       four();
//     }, 4000);
//   };

//   function two(url){
//     page.open(url, function(status){
//     //  console.log(status, url);
//     console.log("opening page 2...");
//       if(status ==='success'){
//         page.evaluate(function(eventObj){
//           document.getElementById('event_title').value = eventObj.title;
//           document.getElementById('event_event_category_id').value = "141421"; // most general 'Workshop' category for now OR 'value' = 141381 for General

//           document.getElementsByName("event[start_date]")[0].value = eventObj.startDate;
//           document.getElementsByName("start-date")[0].value = eventObj.startDate;

//           document.getElementsByName("event[start_date_time]")[0].value = eventObj.startDateTime;


//           document.getElementsByName("event[end_date]")[0].value = eventObj.endDate;
//           document.getElementsByName("end-date")[0].value = eventObj.endDate;

//           document.getElementsByName("event[end_date_time]")[0].value = eventObj.endDateTime;


//           document.getElementsByName("event[address]")[0].value = eventObj.eventLocation;


//           var editor = document.getElementById("cke_1_contents");
//           var iframe = editor.lastChild;
//           var text = iframe.contentWindow.document.getElementsByTagName("body")[0];
//           text.firstChild.innerHTML = eventObj.eventDescription;

//           document.getElementById("event_request_umbrella_wide").click();

//           document.getElementById('event_submit').click();
//       }, eventObj);
//       page.render('page2.png');
//         // everything else on the page
//         var t = setTimeout(function(){
//           three();
//         }, 4000);
//       }
//       else{
//         setTimeout(function(){
//           two(url);
//         }, 4000);
//       }
//     });
//   };


//   function exit() {
//     console.log('Done');
//     phantom.exit();
//   };
// };



// // test values
// var eventObj = {
//   title:"Test Event",
//   startDate:"Mar 1, 2017", // format for OrgSync
//   startDateTime:"1:00 PM",
//   endDate:"Mar 1, 2017",
//   endDateTime:"5:00 PM",
//   eventDescription: "Test event description",
//   eventLocation: "16 Washington Pl, New York, NY 10003",
//   coSponsoringClubs: "List co-sponosring clubs here (SVS, EIA,... etc.)", // list separated by commas
//   eventSpeakers: "Speaker 1, Speaker 2, Speaker 3", // list separated by commas
//   areChargingForAddmission: false,
//   contactInfo: contactInfoObj, // some sort of Person obj from API?
//   advisorEmail: "kc1700@nyu.edu" // this is actuall email from OrgSync
// };

// var get = function(url, cb) {
//     request(url, function(error, response, body) {
//     if (!error)
//       return cb(error, null);

//     return cb(null, JSON.parse(body));
//   });
// };

var getDataFromAPI = function(obj) {
  var contactInfoObj = {};
  var eventObj = {};

  var venueId = obj.relationships.venue.data.id;
  var presentersIds = obj.relationships.presenters.data;
  var presenters = "";

  eventObj['title'] = obj.attributes.title;
  eventObj['startDateTime'] = obj.attributes.startDateTime;
  eventObj['endDateTime'] = obj.attributes.endDateTime;
  eventObj['eventDescription'] =- obj.attributes.description || "";
  eventObj['eventSpeakers'] = "";
  eventObj['contactInfo'] = "dhw249@stern.nyu.edu";
  eventObj['advisorEmail'] = "kc1700@nyu.edu";
  eventObj['areChargingForAddmission'] = false;

  request('https://api.tnyu.org/v3/venues/' + venueId, function(err, res, data) {
    var json_data = JSON.parse(data);
    eventObj['eventLocation'] = json_data.data.attributes.address
  });

  presentersIds.forEach(function(p) {
    request('https://api.tnyu.org/v3/presenters/' + p.id, function(err, res, data) {
      var json_data = JSON.parse(data);

      presenters += json_data.data.attributes.name;
    });
  });

  //eventObj['eventSpeakers'] = presenters.trim(" ").replace(" ", ",")
  console.log(presenters);
  return eventObj;
}

var events = JSON.parse(process.argv[2]);
events.forEach(function(event) {
  var eventObj = getDataFromAPI(event);
  console.log(eventObj);
  //submitEventToOrgsync(eventObj);
});






