function calculateAge(){
const input=document.getElementById("dob").value,result=document.getElementById("ageResult");
if(!input){result.textContent="Please select your date of birth.";return}
const dob=new Date(input+"T00:00:00"),today=new Date();
if(dob>today){result.textContent="Date of birth cannot be in the future.";return}
let years=today.getFullYear()-dob.getFullYear(),months=today.getMonth()-dob.getMonth(),days=today.getDate()-dob.getDate();
if(days<0){months--;days+=new Date(today.getFullYear(),today.getMonth(),0).getDate()}
if(months<0){years--;months+=12}
const totalDays=Math.floor((today-dob)/86400000);
result.textContent=`Completed age: ${years} years, ${months} months, ${days} days. Approx. ${totalDays} days lived.`;
}
function dateDifference(){
const a=document.getElementById("date1").value,b=document.getElementById("date2").value,r=document.getElementById("differenceResult");
if(!a||!b){r.textContent="Please select both dates.";return}
const days=Math.abs(Math.round((new Date(b+"T00:00:00")-new Date(a+"T00:00:00"))/86400000));
r.textContent=`Difference: ${days} day(s).`;
}
function checkEligibility() {
    const dob = document.getElementById("eligDob").value;
    const type = document.getElementById("eligType").value;
    const result = document.getElementById("eligResult");

    if (!dob) {
        result.textContent = "Please select your date of birth.";
        return;
    }

    const birthDate = new Date(dob + "T00:00:00");
    const today = new Date();

    let age = today.getFullYear() - birthDate.getFullYear();

    const month = today.getMonth() - birthDate.getMonth();

    if (
        month < 0 ||
        (month === 0 && today.getDate() < birthDate.getDate())
    ) {
        age--;
    }

    if (type === "passport") {
        if (age < 18) {
            result.textContent = `${age} years (Minor Passport)`;
        } else {
            result.textContent = `${age} years (Adult Passport)`;
        }
    } else {
        const requiredAge = Number(type);

        if (age >= requiredAge) {
            result.textContent = `${age} years - Eligible`;
        } else {
            result.textContent = `${age} years - Not Eligible`;
        }
    }
}