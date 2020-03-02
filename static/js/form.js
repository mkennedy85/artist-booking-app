// Function to validate whether or not element supports multiple values
const isMultiSelect = element => element.options && element.multiple;

// Function for selecting mulitple values if element contains it
const getSelectValues = options => [].reduce.call(options, (values, option) => {
  return option.selected ? values.concat(option.value) : values;
}, []);

// Function for converting elements in a form element to a JSON object
const formToJSON = elements => [].reduce.call(elements, (data, element) => {
  // Conditional for genres as it supports multiple selections
  if (isMultiSelect(element)) {
    data[element.name] = getSelectValues(element);
  } else {
    data[element.name] = element.value;
  }
  return data;
}, {});

document.getElementsByClassName('form')[0].onsubmit = function(e) {
  e.preventDefault();
  const form = document.getElementsByClassName('form')[0];
  const results = formToJSON(form.elements);
  console.log(results)
}