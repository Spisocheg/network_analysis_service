function displayLoad(input) {
    file_name = input.files[0].name;
    csv_file_input_text.innerHTML = `Выбрано: ${file_name}`;
}