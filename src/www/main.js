const message = document.getElementById("message");
const numer = document.getElementById('number');
const author = document.getElementById('author');
const urlParams = new URLSearchParams(window.location.search);

let clientName = urlParams.get('name');
if(clientName == null){
    clientName = "Dear";
}

fetch(`http://3.84.52.187:80/motivate/${clientName}`)
        .then(res => res.json())
        .then(data => {
            message.innerText = data.quote;
            number.innerText = data.id
            author.innerText = data.author
        })
        .catch((error)=>{
            console.log("Error Fetching :", error.message);
    })


