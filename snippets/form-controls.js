// jQuery code for querying/filtering data based on form controls

// Updates the slider when input text values are changed.
$("#edu-textbox, #age-textbox, #gdp-textbox").on("change", function() {
    var eduChange = $("#edu-textbox").val(),
        ageChange = $("#age-textbox").val(),
        gdpChange = $("#gdp-textbox").val();

    $("#edu").val(eduChange);
    $("#age").val(ageChange);
    $("#gdp").val(gdpChange);
});

// Submits form when slider is moved.
$("#edu, #age, #gdp, #order_by, #sort").on("change", function() {
    $("#form").submit();
});

// Reset form to default values.
$("#reset").on("click", function() {
    // Set slider values to 0.
    $("#edu").val(0);
    $("#age").val(0);
    $("#gdp").val(0);

    // Default order and sort by
    $("#order_by").val("edu_index");
    $("#sort").val("DESC");

    // Submit form
    $("#form").submit();
});