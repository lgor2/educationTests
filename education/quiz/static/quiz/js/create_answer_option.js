function* createAnswerOption (whereToAdd) {
  counter = 1;

  while (true) {
      var newTextInput = document.createElement("input");
      newTextInput.type = "text";
      newTextInput.id = "input_text_" + counter;

      var newCheckbox = document.createElement("input");
      newCheckbox.name = "close_one_checkbox_answer";

      if (whereToAdd == 'answers_to_close_one'){
        newCheckbox.type = "radio";
        newCheckbox.value = "close_one_answer_" + counter;
        newTextInput.name = "close_one_answer_" + counter;
      }
      else if (whereToAdd == 'answers_to_close_many') {
        newCheckbox.type = "checkbox";
        newCheckbox.name = "close_many_answer_" + counter;
        newTextInput.name = "close_many_answer_" + counter;
      }

      var newLabel = document.createElement("label");
      newLabel.appendChild(newCheckbox);
      newLabel.appendChild(newTextInput);
      newLabel.classList.add('answer_option_label');

      document.getElementById(whereToAdd).appendChild(newLabel);

      yield counter;
      counter++;
  }
};

// Create a generators object
const ForOneAnswer = createAnswerOption("answers_to_close_one");
const ForManyAnswers = createAnswerOption("answers_to_close_many");

ForOneAnswer.next();
ForManyAnswers.next();

document.getElementById("addButton_one_answer").addEventListener("click", function() {
    ForOneAnswer.next();
});
document.getElementById("addButton_many_answers").addEventListener("click", function() {
    ForManyAnswers.next();
});