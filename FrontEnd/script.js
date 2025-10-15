


/* -----------------------Add Page Name----------------------- */

/* ---------------------- index.html  ----------------------- */
// Function to fetch and display PatronAccount table data
// All pages using PatronAccount table
function fetchTableData() {
    $.ajax({
        url: 'fetch_patron_data.php',
        type: 'GET',
        dataType: 'html',
        success: function (data) {
            $('#tableData').html(data); // Display PatronAccount table data
        },
        error: function () {
            console.error('Failed to fetch PatronAccount data.');
        }
    });
}


// * Patron Form Submission *
// Wait for the document to be fully loaded
$(document).ready(function() {

    // Fetch and display PatronAccount table data when the page loads
    // Page: All pages using PatronAccount table
    fetchTableData();

    // Handle form submission using AJAX
    $('#patronForm').submit(function(event) {
        event.preventDefault(); // Prevent the default form submission

        // Validate the "identityConfirmed" field
        var identityConfirmed = $('#identityConfirmed').val();
        if (identityConfirmed !== "yes") {
            alert('Please confirm identity with "Yes" to submit the form.');
            return;
        }

        // Continue with form submission
        $.ajax({
            url: 'process_patron_form.php',
            type: 'POST',
            data: $('#patronForm').serialize(), // Serialize the form data
            success: function(data) {
                // Update the displayed PatronAccount table data
                fetchTableData();
                // Clear the form fields
                $('#patronForm')[0].reset();

                // Display success message
                alert('Patron added successfully!');
            },
            error: function() {
                console.error('Failed to add a patron.');
            }
        });
    });
});

/* -------------- Phone Number Input Formatting -------------- */

// Wait for the document to be fully loaded
document.addEventListener("DOMContentLoaded", function () {
    // Get the phone number input element
    var phoneNumberInput = document.getElementById("phoneNumber");

    // Add an event listener for input changes
    phoneNumberInput.addEventListener("input", function () {
        // Remove non-numeric characters
        // Page: All pages with a phone number input
        var value = this.value.replace(/\D/g, '');

        // Limit to 10 digits
        if (value.length > 10) {
            value = value.slice(0, 10);
        }

        // Format phone number with dashes
        if (value.length >= 3 && value.length <= 6) {
            value = value.slice(0, 3) + "-" + value.slice(3);
        } else if (value.length > 6) {
            value = value.slice(0, 3) + "-" + value.slice(3, 6) + "-" + value.slice(6);
        }

        // Update the input value with the formatted phone number
        this.value = value;
    });

    // Add an event listener for the Backspace key
    phoneNumberInput.addEventListener("keydown", function (e) {
        if (e.key === "Backspace") {
            // Allow backspace to delete digits
            var value = this.value.replace(/\D/g, ''); // Remove non-numeric characters
            if (value.length >= 4) {
                value = value.slice(0, value.length - 1);
                this.value = value;
            } else {
                this.value = "";
            }
            e.preventDefault();
        }
    });
});

/* -------------- Zipcode Format - 5-digit -------------- */

// Wait for the document to be fully loaded
document.addEventListener("DOMContentLoaded", function () {
    // Get the zipcode input element
    // Page: All pages with a zipcode input
    var zipcodeInput = document.getElementById("zipcode");

    // Add an event listener for input changes
    zipcodeInput.addEventListener("input", function () {
        // Remove non-numeric characters
        var value = this.value.replace(/\D/g, '');

        // Limit to 5 characters
        if (value.length > 5) {
            value = value.slice(0, 5);
        }

        // Update the input value with the formatted zipcode
        this.value = value;
    });
});

/* -------------- State Required Field - For United States Only -------------- */

// Wait for the document to be fully loaded
document.addEventListener("DOMContentLoaded", function () {
    // Get the country and state input elements
    // Page: All pages with country and state inputs
    var countrySelect = document.getElementById("country");
    var stateInput = document.getElementById("state");

    // Add an event listener for the country select input
    countrySelect.addEventListener("change", function () {
        if (this.value === "United States") {
            // Enable state input if United States is selected
            stateInput.removeAttribute("disabled");
        } else {
            // Clear the state input and disable it for non-U.S. countries
            stateInput.value = "";
            stateInput.setAttribute("disabled", "disabled");
        }
    });
});









$(document).ready(function () {
    /* ----------------------- catalog.html ----------------------- */

    // Function to fetch and display Inventory table data
    function fetchInventoryTableData() {
        $.ajax({
            url: 'inventory.php',
            type: 'GET',
            dataType: 'html',
            success: function (data) {
                $('#inventoryTable tbody').html(data);
            },
            error: function () {
                console.error('Failed to fetch Inventory table data.');
            }
        });
    }

    // Function to automatically insert 1 into the In Stock input field in the form
    function setDefaultInStockValue() {
        // Assuming you have an input field with id "inStock" in your form
        $("#inStock").val(1);
    }




    // Add an event listener to the "Add Item" button
    $("#addItemBtn").click(function () {
        var addItemForm = $("#addItemFormContainer");
        addItemForm.css("display", "block");

        // Call the function to set the default In Stock value
        setDefaultInStockValue();
    });

    // Add an event listener to the "Close" button
    $("#closeFormBtn").click(function () {
        var addItemForm = $("#addItemFormContainer");
        addItemForm.css("display", "none");
    });

    // Function to show a notification
    function showNotification(message) {
        alert(message);
    }

    // Add an event listener for the "Add 1" button in the table
    $(document).on('click', '.add-button', function () {
        var itemIdToAdd = $(this).data("id");

        // AJAX request to increment the in-stock value for an item
        $.ajax({
            url: 'add_one.php',
            type: 'POST',
            data: {itemId: itemIdToAdd},
            success: function () {
                // Update the in-stock value in the table and show a notification
                var inStockCell = $("#inventoryTableBody tr[data-id='" + itemIdToAdd + "'] td.inStock");
                var titleCell = $("#inventoryTableBody tr[data-id='" + itemIdToAdd + "'] td.title");

                if (inStockCell.length > 0 && titleCell.length > 0) {
                    // Get the current In Stock value and increment by 1
                    var currentInStock = parseInt(inStockCell.text());
                    inStockCell.text(currentInStock + 1);

                    // Show a notification with the added book's title
                    var addedTitle = titleCell.text();
                    showNotification('Another copy of "' + addedTitle + '" has been added.');
                } else {
                    console.error('Could not find the In Stock or Title cell for item with ID:', itemIdToAdd);
                    console.log('Row HTML:', $("#inventoryTableBody tr[data-id='" + itemIdToAdd + "']").html());
                }
            },
            error: function () {
                console.error('Failed to add a book to item with ID: ' + itemIdToAdd);
            },
            complete: function () {
                // Fetch and display updated inventory table data
                fetchInventoryTableData();
            }
        });
    });

    $(document).ready(function () {
        // Function to generate and display the label
        function generateLabel() {
            // Get form data
            var title = $("#title").val();
            var author = $("#author").val();
            var year = $("#year").val();
            var locCode = $("#locCode").val();
            var shelfCode = $("#shelfCode").val();
            var cost = $("#cost").val();
            var itemType = $("#itemType").val();
            var branch = $("#branch").val();

            // Create label content
            var labelContent = "Title: " + title + "<br>" +
                "Author: " + author + "<br>" +
                "Year: " + year + "<br>" +
                "Library of Congress Code: " + locCode + "<br>" +
                "Shelf Location Code: " + shelfCode + "<br>" +
                "Cost: " + cost + "<br>" +
                "Item Type: " + itemType + "<br>" +
                "Branch: " + branch;

            // Open a small popup window with the label content
            var labelWindow = window.open('', '_blank', 'width=300,height=400,scrollbars=yes,resizable=yes');
            labelWindow.document.write('<html><head><title>Label</title></head><body>' + labelContent +
                '<br><button id="printBtn">Print</button>' +
                '<button id="closeBtn">Close</button>' +
                '</body></html>');
            labelWindow.document.close();

            // Attach click event to the Print button in the popup window
            labelWindow.document.getElementById('printBtn').addEventListener('click', function () {
                labelWindow.print();
            });

            // Attach click event to the Close button in the popup window
            labelWindow.document.getElementById('closeBtn').addEventListener('click', function () {
                labelWindow.close();
            });
        }

        // Event listener for the Generate Label button
        $("#generateLabelBtn").click(function () {
            generateLabel();
        });
    });

// Add an event listener for the "Delete" button in the table
    $(document).on('click', '.delete-button', function () {
        var itemIdToDelete = $(this).data("id");

        // AJAX request to delete or update an item
        $.ajax({
            url: 'delete_item.php',
            type: 'POST',
            data: {itemId: itemIdToDelete},
            success: function (data) {
                // Handle the response and update the table accordingly
                if (data === 'deleted') {
                    // If the item is deleted from the database, remove it from the table
                    var inStockCell = $("#inventoryTableBody tr[data-id='" + itemIdToDelete + "'] td.inStock");

                    if (inStockCell.length > 0) {
                        var currentInStock = parseInt(inStockCell.text());

                        // Check if inStock is 1
                        if (currentInStock === 1) {
                            // Prompt the user with a confirmation dialog
                            var confirmDelete = confirm('This is the last copy. Do you want to delete it from the database as well?');

                            if (confirmDelete) {
                                // User clicked "Yes," proceed with both database deletion and table removal
                                $.ajax({
                                    url: 'delete_item.php',
                                    type: 'POST',
                                    data: {itemId: itemIdToDelete},
                                    success: function () {
                                        $("#inventoryTableBody tr[data-id='" + itemIdToDelete + "']").remove();
                                        alert('Item deleted from the database and removed from the table.');
                                    },
                                    error: function () {
                                        console.error('Failed to delete item with ID:', itemIdToDelete);
                                    }
                                });
                            } else {
                                // User clicked "No," do nothing
                                alert('Item not deleted.');
                            }
                        } else {
                            // If inStock is not 1, remove only from the table
                            $("#inventoryTableBody tr[data-id='" + itemIdToDelete + "']").remove();
                            alert('Item removed from the table.');
                        }
                    } else {
                        console.error('Could not find the In Stock cell for item with ID:', itemIdToDelete);
                    }
                } else if (data === 'updated') {
                    // If the item is updated in the database, update the inStock value in the table
                    var inStockCell = $("#inventoryTableBody tr[data-id='" + itemIdToDelete + "'] td.inStock");
                    var titleCell = $("#inventoryTableBody tr[data-id='" + itemIdToDelete + "'] td.title");

                    if (inStockCell.length > 0 && titleCell.length > 0) {
                        // Get the current In Stock value and decrement by 1
                        var currentInStock = parseInt(inStockCell.text());
                        inStockCell.text(currentInStock - 1);

                        // Show a notification with the removed book's title
                        var removedTitle = titleCell.text();
                        showNotification('1 copy of "' + removedTitle + '" has been removed.');
                    } else {
                        console.error('Could not find the In Stock or Title cell for item with ID:', itemIdToDelete);
                        console.log('Row HTML:', $("#inventoryTableBody tr[data-id='" + itemIdToDelete + "']").html());
                    }
                } else {
                    console.error('Failed to delete or update item with ID: ' + itemIdToDelete);
                }
            },
            error: function () {
                console.error('Failed to delete or update item with ID: ' + itemIdToDelete);
            }
        });
    });

    // Flag to track whether form submission is in progress
    var isFormSubmitting = false;

    // Fetch and display inventory data on page load
    $(document).ready(function () {
        fetchInventoryTableData();

        // Handle form submission using AJAX
        $('#addItemFormContainer form').off('submit').on('submit', function (event) {
            event.preventDefault(); // Prevent the default form submission

            // Check if form submission is already in progress
            if (isFormSubmitting) {
                console.log('Form submission is already in progress.');
                return;
            }

            // Set the flag to indicate form submission is in progress
            isFormSubmitting = true;

            // Continue with form submission
            $.ajax({
                url: 'inventory.php',
                type: 'POST',
                data: $(this).serialize(),
                success: function (data) {
                    // Check the response from the server
                    if (data.includes('success')) {
                        // If the response contains 'success', the item was added successfully
                        showNotification('Item added successfully.');
                        fetchInventoryTableData(); // Update the displayed inventory table data
                        $('#addItemFormContainer').css("display", "none");
                        $('#addItemFormContainer form')[0].reset();
                    } else {
                        // If the response does not contain 'success', there was an error
                        console.error('Failed to add an item. Server response:', data);
                        showNotification('Failed to add an item. Please try again.');
                    }
                },
                error: function () {
                    console.error('Failed to add an item.');
                    showNotification('Failed to add an item. Please try again.');
                },
                complete: function () {
                    // Reset the flag after the form submission is complete
                    isFormSubmitting = false;
                }
            });
        });

        // Add an event listener to the search input for real-time search
        $("#searchInput").on('input', function () {
            performSearch();
        });

        // Add an event listener for the search button
        $("#searchBtn").click(function (event) {
            event.preventDefault(); // Prevent the form from submitting (if it's inside a form)
            performSearch();
        });

        // Function to perform the search and update the table
        function performSearch() {
            var searchInput = $("#searchInput").val();
            var searchCriteria = $("#searchCriteria").val();

            // Perform AJAX request to fetch filtered data
            $.ajax({
                url: 'fetch_inventory_data.php',
                type: 'GET',
                data: {searchInput: searchInput, searchCriteria: searchCriteria},
                dataType: 'html',
                success: function (data) {
                    $('#inventoryTable tbody').html(data);
                },
                error: function () {
                    console.error('Failed to fetch filtered inventory data.');
                }
            });
        }

        // Set the default duration to 14
        $('#duration').val(14);

        // Add an event listener to the itemType dropdown for real-time duration calculation
        $('#itemType').off('change').on('change', function () {
            // Get the selected item type
            var itemType = $(this).val();

            // Set the duration based on the selected item type
            var duration = (itemType === 'Book') ? 14 : ((itemType === 'DVD') ? 3 : 0);

            // If the duration is not set based on item type, keep the default value (14)
            duration = duration || 14;

            // Set the calculated duration in the duration input field
            $('#duration').val(duration);
        });

        // Add an event listener to the cost input for real-time late fee calculation
        $('#cost').off('input').on('input', function () {
            // Get the cost entered by the user
            var cost = parseFloat($(this).val());

            // Calculate 10% of the cost as late fee
            var lateFee = 0.1 * cost;

            // Set the calculated late fee in the lateFee input field
            $('#lateFee').val(lateFee.toFixed(2));
        });
    });



    /* ----------------------- checkout.html ----------------------- */

    // Function to populate patron dropdown
    function populatePatronDropdown(dropdown, data, defaultText) {
        dropdown.empty();
        dropdown.append($('<option>', {
            value: '',
            text: defaultText,
            disabled: true,
            selected: true
        }));

        $.each(data, function (index, value) {
            dropdown.append($('<option>', {
                value: value.patronID,
                text: `${value.patronID} - ${value.firstName} ${value.lastName}`
            }));
        });
    }

    // Function to populate item dropdown
    function populateItemDropdown(dropdown, data, defaultText) {
        dropdown.empty();
        dropdown.append($('<option>', {
            value: '',
            text: defaultText,
            disabled: true,
            selected: true
        }));

        $.each(data, function (index, value) {
            dropdown.append($('<option>', {
                value: value.itemID,
                text: `${value.itemID} - ${value.title} - ${value.author} - ${value.itemType}`
            }));
        });
    }

    $.ajax({
        url: 'checkout.php',
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            console.log('Data received:', data);
            var patronDropdown = $('#patronID');
            var itemDropdown = $('#itemID');

            // Populate patron dropdown
            populatePatronDropdown(patronDropdown, data.patronData, 'Select Patron');

            // Populate item dropdown
            populateItemDropdown(itemDropdown, data.itemData, 'Select Item');
        },
        error: function (xhr, status, error) {
            console.error('Failed to fetch data. Status:', status, 'Error:', error);
        }
    });
});


/* -----------------------home.html showing tables----------------------- */
$(document).ready(function () {
    function fetchTableData(tableId, fetchScript) {
        console.log('Fetching data for table:', tableId);
        $.ajax({
            url: fetchScript,
            type: 'GET',
            dataType: 'html',
            success: function (data) {
                console.log('Data received:', data);
                $('#' + tableId + 'Body').html(data);
            },
            error: function () {
                console.error('Failed to fetch data for table:', tableId);
            }
        });
    }

    // Fetch Checkout Table Data
    fetchTableData('checkoutTable', 'fetch_checkout_data.php');

});


/* -----------------------patron page // index.html ----------------------- */
$(document).ready(function () {
    function fetchPatronTableData() {
        console.log('Fetching patron data...');
        $.ajax({
            url: 'fetch_patron_data.php',
            type: 'GET',
            dataType: 'html',
            success: function (data) {
                console.log('Data received:', data);
                $('#patronTable').html(data);
            },
            error: function () {
                console.error('Failed to fetch Patron table data.');
            }
        });
    }

    fetchPatronTableData();
});

/* -----------------------Add Page Name----------------------- */
/* -----------------------Add Page Name----------------------- */
