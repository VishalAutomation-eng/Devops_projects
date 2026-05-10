async function calculateResult() {

    const number1 = document.getElementById("number1").value;
    const number2 = document.getElementById("number2").value;

    const response = await fetch(
        `http://127.0.0.1:8000/calculate?a=${number1}&b=${number2}`
    );

    const data = await response.json();

    document.getElementById("result").innerHTML = `
        <p>Addition: ${data.addition}</p>
        <p>Subtraction: ${data.subtraction}</p>
        <p>Multiplication: ${data.multiplication}</p>
    `;
}