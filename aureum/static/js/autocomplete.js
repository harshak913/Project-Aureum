/*An array containing all the companies:*/
var countries = companies;

/*initiate the autocomplete function on the "myInput" element, and pass along the countries array as possible autocomplete values:*/
autocomplete(document.getElementById("myInput"), countries);

/*PRESERVE THIS FUNCTION FOR THROWING AN ERROR*/
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
