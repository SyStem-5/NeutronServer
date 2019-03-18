let applications = {};
let version_control_data = {};

const apptable = $('#app_table');

function generate_accordion(app_id) {
    const col_span = $("<td colspan='3' nowrap>");
    const accordion_div = $("<div class='collapse'>").attr('id', `accordion${app_id}`);
    const grid_container = $("<div class='grid-container' style='grid-template-columns:auto auto auto; display: grid; grid-gap: 1em;'>");

    accordion_div.append(grid_container);
    col_span.append(accordion_div);
    return col_span;
}

function populate_applist() {
    const vc_data_copy = jQuery.extend(true, {}, version_control_data);

    if (jQuery.isEmptyObject(applications)) {
        console.debug('Server returned empty application list.');
        const info = $('<br><li nowrap>No registered applications found.</li><br>');
        apptable.append(info);
        return;
    }

    let counter = 1;
    Object.keys(applications).forEach((app) => {
        let app_ver_data = {};

        Object.keys(vc_data_copy).forEach((ver_data) => {
            if (vc_data_copy[ver_data].application_id === applications[app].id) {
                app_ver_data = vc_data_copy[ver_data];
                delete vc_data_copy[ver_data];
            }
        });

        const table_row = $("<tr data-toggle='collapse' class='clickable'></tr>")
            .attr('data-target', `#accordion${applications[app].id}`);
        const row_id = $('<td></td>').text(counter);
        const app_name = $('<td></td>').text(applications[app].name);
        const last_updated = $('<td></td>').text(app_ver_data.last_updated);

        // var btn = $("<td style='text-align:right' data-toggle='collapse' data-target=
        // '#accordion25' class='clickable'><button class='btn mdi mdi mdi-details'></button></td>");
        table_row.append(row_id, app_name, last_updated /* btn */);

        const table_row_accordion = $('<tr></tr>');
        const accordion = generate_accordion(applications[app].id);

        Object.keys(app_ver_data.versions).forEach((branch) => {
            const new_grid_item = $("<div class='grid-item'>");

            const branch_label = $("<div style='text-align:center'></div>").text(branch);

            const component_label = $("<div style='text-align:center'></div>");
            Object.keys(app_ver_data.versions[branch]).forEach((component) => {
                if (jQuery.isEmptyObject(app_ver_data.versions[branch][component]) || app_ver_data.versions[branch][component][0].version === '0.0.0') {
                    component_label.append(`${component} -> No version published<br>`);
                } else {
                    component_label.append(`${component} -> V${app_ver_data.versions[branch][component][0].version}<br>`);
                }
            });

            new_grid_item.append(branch_label, component_label);
            accordion.find('.grid-container').append(new_grid_item);

            table_row_accordion.append(accordion);

            apptable.append(table_row, table_row_accordion);
            counter += 1;
        });
    });
}

$.getJSON('get/all')
    .done((json) => {
        applications = json.applications_data;
        version_control_data = json.version_control;

        console.debug('Successfuly fetched json.');
        populate_applist();
    })
    .fail((jqxhr, textStatus, error) => {
        console.error(error);
    });
