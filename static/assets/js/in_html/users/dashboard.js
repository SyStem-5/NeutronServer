/* eslint-disable indent */
/* eslint-disable no-undef */
// let elements = $("[id^=updaters_list-]");
let vc_apps = [];
let user_list = [];
let user_updaters = [];

const main_table = $("#usertable");

$.getJSON("/users/get")
    .done((json) => {
        user_list = json["users"];
        console.debug("Successfully fetched user data.");

        $.getJSON("/users/updaters/get")
            .done((json) => {
                user_updaters = json["users"];
                console.debug("Successfully fetched user updater data.");
                populate_list();
            })
            .fail((jqxhr, textStatus, error) => {
                console.error(error);
            });
    })
    .fail((jqxhr, textStatus, error) => {
        console.error(error);
    });

$.getJSON("/versioncontrol/get/apps")
    .done((json) => {
        vc_apps = json.applications_data;

        console.debug("Successfully fetched application data.");
    })
    .fail((jqxhr, textStatus, error) => {
        console.error(error);
    });

function populate_list() {
    user_list.forEach(user => {
        const user_pk = user.pk;
        user = user.fields;

        let user_updater = null;
        user_updaters.forEach(updaters => {
            if (updaters.pk == user_pk) {
                user_updater = updaters;
            }
        });

        generate_user_table_row(user_pk, user.username, user.first_name, user.last_name, user.email, user_updater["fields"]["updaters"]);
    });
}

function generate_user_table_row(id, username, firstname, lastname, email, registered_updaters) {
    let registered_updaters_num = 0;

    if (!jQuery.isEmptyObject(registered_updaters)) {
        registered_updaters_num = Object.keys(registered_updaters["updaters"]).length;
    }

    const table_row = $("<tr></tr>");
    const user_id_col = $("<td></td>").text(id);
    const first_last_name_col = $("<td></td>").html(`${escapeHtml(firstname)} ${escapeHtml(lastname)}`);
    const username_col = $("<td></td>").text(username);
    const email_col = $("<td></td>").text(email);
    const registered_updaters_num_col = $("<td data-toggle='collapse' class='clickable'></td>").text(registered_updaters_num).attr("data-target", `#accordion_${id}`);

    const action_button = $("<button type='button' class='btn btn-custom dropdown-toggle waves-effect waves-light' data-toggle='dropdown' aria-expanded='false'> </button>");
    const action_button_dropdown = $("<div class='dropdown-menu dropdown-menu-right'>");
    const dropdown_item = $("<a href='javascript:void(0);' class='dropdown-item'>Register updater</a>");
    dropdown_item.on("click", function() {
        generate_updaters_modal_new(username);
    });
    action_button_dropdown.append(dropdown_item);

    table_row.append(user_id_col, first_last_name_col, username_col, email_col, registered_updaters_num_col, action_button, action_button_dropdown);

    $(main_table).append(table_row);

    if (registered_updaters_num > 0) {
        const table_row_accordion = $("<tr></tr>");

        const accordion = $("<td colspan='5' nowrap>");
        const accordion_div = $("<div class='collapse'>").attr("id", `accordion_${id}`);
        const table_resp = $("<div class='table-responsive'>");
        const table_main = $("<table class='tablesaw table table-hover'>");
        const thead = `
        <thead>
            <tr>
                <th>Identifier</th>
                <th>Application</th>
                <th>Branch</th>
                <th>Component(s)</th>
            </tr>
        </thead>
        `;
        table_main.append(thead);

        const updater_list = generate_updater_table(registered_updaters["updaters"]);
        table_main.append(updater_list);

        table_resp.append(table_main);
        accordion_div.append(table_resp);
        accordion.append(accordion_div);

        table_row_accordion.append(accordion);

        $(main_table).append(table_row_accordion);
    }
}

function generate_updater_table(updaters) {
    let main_obj = $("<tbody>");
    Object.keys(updaters).forEach(identifier => {
        Object.keys(updaters[identifier]).forEach(app => {
            Object.keys(updaters[identifier][app]).forEach(branch => {
                const components = updaters[identifier][app][branch].join(", ");

                const table_row = $("<tr></tr>");
                const id_col = $("<td></td>").text(identifier);
                const app_col = $("<td></td>").text(app);
                const branch_col = $("<td></td>").text(branch);
                const components_col = $("<td></td>").text(components);

                table_row.append(id_col, app_col, branch_col, components_col);
                main_obj.append(table_row);
            });

        });
    });

    return main_obj;
}

function generate_updaters_modal_new(username) {
    // Generate a modal for creating new updaters
    // The submit function triggers an AJAX request

    // username is sent to the server -> then the server creates the MQTT username for the updater
    // password is generated on the server and is returned to the client along with the generated MQTT username

    // generate a checkmark tree
    /*
    <APP_NAME>
        <BRANCH_NAME>
            <COMPONENT>
    */

    $("#updater_new_modal").remove();

    let html = `
    <div class="modal fade" role="dialog" tabindex="-1" style="" id="updater_new_modal">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header d-block">
                    <div class="d-flex">
                        <h3 class="modal-title">Generate a new updater</h4>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">×</span>
                        </button>
                    </div>
                    <h5 class="modal-title">User: '${escapeHtml(username)}'</h5>
                </div>
                <div class="modal-body">

                    <div id="${escapeHtml(username)}_generated" hidden>
                        <h4 class="m-t-0 header-title">Credentials</h4>
                        <p class="text-muted m-b-5 font-15">
                            Generated Indentifier: <code id="${escapeHtml(username)}_generated_identifier" class="highlighter-rouge"></code>
                        </p>
                        <p class="text-muted m-b-30 font-15">
                            Generated Password: <code id="${escapeHtml(username)}_generated_password" class="highlighter-rouge"></code>
                        </p>
                    </div>

                    <ul id="updater_new_${escapeHtml(username)}" class="checktree">`;
                        vc_apps.forEach(app => {
                            let subHtml = `
                            <li>
                                <input id="${escapeHtml(app.name)}" type="checkbox" />
                                <label style="display: contents !important;">
                                        &nbsp${escapeHtml(app.name)}
                                </label>
                                <ul>`;
                                app.branches["branches"].forEach(branch => {
                                        subHtml += `
                                        <li>
                                            <input id="${escapeHtml(app.name)}:${escapeHtml(branch)}"
                                                type="checkbox"/>
                                            <label style="display: contents !important;">
                                                &nbsp${escapeHtml(branch)}
                                            </label>`;

                                            app.components["components"].forEach(component => {
                                                subHtml += `
                                                <ul>
                                                    <input id="${escapeHtml(app.name)}:${escapeHtml(branch)}:${escapeHtml(component)}"
                                                        type="checkbox" />
                                                    <label style="display: contents !important;">
                                                        &nbsp${escapeHtml(component)}
                                                    </label>
                                                </ul>`;
                                            });

                            subHtml += "</li>";
                                });
                    subHtml += `</ul>
                            </li>`;

                            html += subHtml;
                        });

            html += `</ul>
                </div>
                <div class="modal-footer">
                    <button id="btn-generate-updater" type="button" class="btn btn-primary btn-block" for="updater_new_${escapeHtml(username)}">Generate</button>
                </div>
            </div>
        </div>
    </div>`;

    $("body").append(html);
    $("#updater_new_modal").modal();

    $("#btn-generate-updater").on("click", function() {
        /*
        "LSOC": {
            "stable": ["NeutronCommunicator", "BlackBox", "WebInterface"],
            "beta": ["NeutronCommunicator", "BlackBox", "WebInterface"]
        }
        */
        const username = $(this).attr("for").split("updater_new_")[1];
        let updaters = {};
        let vc_apps_sorted = {};

        vc_apps.forEach(app => {
            vc_apps_sorted[app.name] = {};
            vc_apps_sorted[app.name]["branches"] = app.branches.branches;
            vc_apps_sorted[app.name]["components"] = app.components.components;
        });

        Array.from($(`#${$(this).attr("for")}`).children("li")).forEach(list => {
            const main_input = $(list).children("input");
            if (main_input.is(":checked")) {
                const main_input_id = main_input.attr("id");
                if (!updaters[main_input_id]) {
                    updaters[main_input_id] = {};
                }
                // Add every branch and every component to every branch of this app
                vc_apps_sorted[main_input_id]["branches"].forEach(branch => {
                    updaters[main_input_id][branch] = vc_apps_sorted[main_input_id]["components"];
                });
            } else {
                Array.from($(list).children("ul").children("li")).forEach(branch => {
                    const branch_input = $(branch).children("input");
                    if (branch_input.is(":checked")) {
                        const branch_input_id = branch_input.attr("id").split(":")[1];
                        if (!updaters[main_input.attr("id")]) {
                            updaters[main_input.attr("id")] = {};
                        }
                        // Add every component of this branch
                        updaters[main_input.attr("id")][branch_input_id] = vc_apps_sorted[main_input.attr("id")]["components"];
                    } else {
                        Array.from($(branch).children("ul")).forEach(component => {
                            const component_input = $(component).children("input");

                            if(component_input.is(":checked")) {
                                // Add this component
                                const component_input_id = component_input.attr("id").split(":")[2];
                                const branch_input_id = branch_input.attr("id").split(":")[1];

                                if (!updaters[main_input.attr("id")]) {
                                    updaters[main_input.attr("id")] = {};
                                }

                                if (!updaters[main_input.attr("id")][branch_input_id]) {
                                    updaters[main_input.attr("id")][branch_input_id] = [];
                                }
                                updaters[main_input.attr("id")][branch_input_id].push(component_input_id);
                            }
                        });
                    }

                });
            }
        });

        if (jQuery.isEmptyObject(updaters)) {
            return;
        }

        // Send the data to the backend
        $.ajax({
            url: "/users/updaters/new",
            type: "POST",

            // Form data
            data: {csrfmiddlewaretoken: $("#csrf_token").children("input").attr("value"), username: username, data: JSON.stringify(updaters)},

            success: function (result) {
                if (result["result"] === true) {
                    $(`#${username}_generated_identifier`).text(result["username"]);
                    $(`#${username}_generated_password`).text(result["password"]);
                    $(`#${username}_generated`).removeAttr("hidden");
                } else {
                    console.error(result["msg"]);
                }
            },
            fail: function (result) {
                console.log("error " + result);
            }
        });
    });

    $(document).on("change", "input[type='checkbox']", function (event) {
        event.stopPropagation();

        const elem_id = event.target.id;

        if ((elem_id.split(":").length - 1) != 2) {

            var clkCheckbox = $(this);
            var chkState = clkCheckbox.is(":checked");

            var children = clkCheckbox.closest("li");

            children.find(":checkbox").prop("checked", chkState);
        } else {
            const chkState = $(this).is(":checked");
            const siblings = $(this).parent("ul").siblings("ul");
            let states = [chkState];

            Array.from(siblings).forEach(sibling => {
                states.push($(sibling).children("input").is(":checked"));
            });

            if (states.every(function(item){return item == true;})) {
                $(this).parent("ul").siblings("input").prop("checked", true);
            } else {
                $(this).parent("ul").siblings("input").prop("checked", false);
            }
        }
    });
}
