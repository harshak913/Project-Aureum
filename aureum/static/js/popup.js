function myFunction() {
  var popup = document.getElementById("myPopup");
  popup.classList.toggle("show");
}

function mySubmitFunction(e)
{
  var company = document.getElementById("tags").value;
  var company_exist = countries.includes(company);
  if (countries.includes(company) === false){
    alert('Company Name or Ticker Not Valid');
    e.preventDefault();
    return false;
  }
}
