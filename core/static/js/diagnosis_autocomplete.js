$(document).ready(function() {
    $("#id_icd_code").autocomplete({
        source: function(request, response) {
            $.ajax({
                url: "/ajax/icd11-autocomplete/",
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
                    response($.map(data, function(item) {
                        return {
                            label: item.Code + " - " + item.Title,
                            value: item.Code,
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
            $("#id_icd_code").val(data.Code);
            fetchAndPopulateICDDetails(data.Code);
            return false;
        }
    });

    // Handle manual code entry
    $("#id_icd_code").on('change', function() {
        const code = $(this).val().trim();
        if (code.length >= 2) {
            fetchAndPopulateICDDetails(code);
        }
    });

    // Function to fetch complete ICD details and populate all form fields
    function fetchAndPopulateICDDetails(code) {
        $.ajax({
            url: "/ajax/icd11-details/",
            dataType: "json",
            data: {
                code: code
            },
            success: function(data) {
                if (data.error) {
                    console.error("ICD-11 details error:", data.error);
                    return;
                }
                
                // Populate all form fields with the data
                $("#id_name").val(data.Title || '');
                $("#id_description").val(data.Description || '');
                $("#id_inclusions").val(data.Inclusions || '');
                $("#id_exclusions").val(data.Exclusions || '');
                $("#id_foundation_uri").val(data["Foundation URI"] || '');
                $("#id_index_terms").val(data["Index Terms"] || '');
                $("#id_coded_elsewhere").val(data["Coded Elsewhere"] || '');
                $("#id_related_maternal_codes").val(data["Related Maternal Codes"] || '');
                $("#id_related_perinatal_codes").val(data["Related Perinatal Codes"] || '');
                $("#id_postcoordination_options").val(data["Postcoordination Options"] || '');
                $("#id_additional_notes").val(data["Additional Notes"] || '');
                $("#id_external_reference_link").val(data["External Reference Link"] || '');
                $("#id_icd_chapter").val(data["ICD Chapter"] || '');
                
                console.log("Populated ICD-11 data:", data);
            },
            error: function(xhr, status, error) {
                console.error("ICD-11 details request failed:", error);
            }
        });
    }
});