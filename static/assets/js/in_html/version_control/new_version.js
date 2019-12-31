/* eslint-disable no-undef */
var applications = {};
var version_control = {};

var selected_app = {};
var selected_vc = {};


$("#inputUpdateRecipe").on("change", function () {
    if ($(this).val() == "" || undefined) {
        $("#helptext_updaterecipe").html("Update recipe will be generated automatically.");
    } else {
        $("#helptext_updaterecipe").html("<b>The system will use this update recipe instead of the automatically generated one.</b>");
    }
});

$("#clearUpdateRecipe").on("click", function () {
    $("#inputUpdateRecipe").val("").trigger("change");
});

$("#inputApp").on("change", function () {

    for (const app in applications) {
        if (applications[app]["id"] == this.value) {
            selected_app = applications[app];
        }
    }

    for (const vc in version_control) {
        if (version_control[vc]["application_id"] == selected_app["id"]) {
            selected_vc = version_control[vc];
        }
    }
    populate_branch_input();
    populate_component_input();
});

$("#inputAppBranch").on("change", function () {
    update_version_number_field();
});

$("#inputAppComponent").on("change", function () {
    update_version_number_field();
});

$.getJSON("get/all")
    .done(function (json) {
        applications = json["applications_data"];
        version_control = json["version_control"];

        console.debug("Successfuly fetched json.");
        populate_app_input();
    })
    .fail(function (jqxhr, textStatus, error) {
        console.error(error);
    });

function populate_app_input() {
    console.debug("Populating app input...");

    $("#inputApp").append(
        "<option value='' disabled selected>Select an application</option>"
    );

    for (const app_num in applications) {
        $("#inputApp").append(
            "<option value='" + applications[app_num]["id"] + "'>" + applications[app_num]["name"] + "</option>"
        );
    }
}

function populate_branch_input() {
    try {
        $("#inputAppBranch").html("");
        $("#inputAppBranch").append(
            "<option value='' disabled selected>Select a branch</option>"
        );

        selected_app["branches"]["branches"].forEach(branch => {
            $("#inputAppBranch").append(
                "<option value='" + branch + "'>" + branch + "</option>"
            );
        });
    } catch (error) {
        console.error(error);
    }
}

function populate_component_input() {
    try {
        $("#inputAppComponent").html("");
        $("#inputAppComponent").append(
            "<option value='' disabled selected>Select the application component</option>"
        );

        selected_app["components"]["components"].forEach(component => {
            $("#inputAppComponent").append(
                "<option value='" + component + "'>" + component + "</option>"
            );
        });
    } catch (error) {
        console.error(error);
    }
}

function update_version_number_field() {
    selected_branch = $("#inputAppBranch").val();

    if ($("#inputAppComponent").val() != null) {
        selected_component = $("#inputAppComponent").val();

        try {
            version = selected_vc["versions"][selected_branch][selected_component] [selected_vc["versions"][selected_branch][selected_component].length-1] ["version"];
        } catch (error) {
            console.log("Couldn't find any version number for this component. Using '0.0.0'.");
            version = "0.0.0";
        }


        $("#inputVersionNumber").val(version);
    }
}


$("#infoForm").submit(function (e) {
    $("#responseMessage").html("");
    e.preventDefault();

    $("#responseMessage").css("color", "white");
    $("#responseMessage").html("Waiting for response from server...");

    console.debug("Submit button clicked");

    $("#progressUpdatePackage").removeAttr("hidden");
    $.ajax({
        url: "/versioncontrol/new",
        type: "POST",

        // Form data
        data: new FormData($("form#infoForm")[0]),

        success: function (data) {
            if (data["result"] === true) {
                $("#responseMessage").css("color", "green");
                $("#responseMessage").html(data["msg"]);
            } else {
                $("#responseMessage").css("color", "red");
                $("#responseMessage").html(data["msg"]);
            }
        },
        fail: function (data) {
            $("#responseMessage").css("color", "red");
            $("#responseMessage").text(data["msg"]);
        },
        // Tell jQuery not to process data or worry about content-type
        // You *must* include these options!
        cache: false,
        contentType: false,
        processData: false,

        // Custom XMLHttpRequest
        xhr: function () {
            var myXhr = $.ajaxSettings.xhr();
            if (myXhr.upload) {
                // For handling the progress of the upload
                myXhr.upload.addEventListener("progress", function (e) {
                    if (e.lengthComputable) {
                        $("#progressUpdatePackage").attr({
                            value: e.loaded,
                            max: e.total,
                        });
                    }
                }, false);
            }
            return myXhr;
        }
    });
});
