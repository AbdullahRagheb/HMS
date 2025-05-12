$(document).ready(function() {
    $("#id_icd_code").autocomplete({
        source: function(request, response) {
            $.ajax({
                url: "{% url 'manager:icd11_autocomplete' %}",
                dataType: "json",
                data: {
                    q: request.term
                },
                success: function(data) {
                    if (data.error) {
                        console.error("ICD-11 API error:", data.error);
                        alert("ICD-11 autocomplete failed. Please enter the code manually using the ICD-11 Browser: https://icd.who.int/browse11/l-m/en");
                        response([]);
                        return;
                    }
                    response($.map(data.results, function(item) {
                        return {
                            label: item.code + " - " + item.title,
                            value: item.code,
                            data: item
                        };
                    }));
                },
                error: function(xhr, status, error) {
                    console.error("Autocomplete request failed:", error);
                    alert("ICD-11 autocomplete failed. Please enter the code manually using the ICD-11 Browser: https://icd.who.int/browse11/l-m/en");
                    response([]);
                }
            });
        },
        minLength: 2,
        select: function(event, ui) {
            var data = ui.item.data;
            $("#id_icd_code").val(data.code);
            $("#id_name").val(data.title);
            $("#id_description").val(data.description || '');
            $("#id_foundation_uri").val(data.foundation_uri || '');
            $("#id_icd_chapter").val(data.chapter || '');
            console.log("Selected ICD-11 data:", data);
            return false;
        }
    });
});