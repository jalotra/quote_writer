const message = document.getElementById("message");
const numer = document.getElementById('number');
const author = document.getElementById('author');

let clientName = window.location.pathname.split("/")[1]

fetch(`http://localhost:80/motivate/${clientName}`)
        .then(res => res.json())
        .then(data => {
            message.innerText = data.quote;
            number.innerText = data.id
            author.innerText = data.author
        })
        .catch((error)=>{
            console.log("Error Fetching :", error.message);
    })


