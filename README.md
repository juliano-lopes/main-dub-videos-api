# Componente 3 - API principal para aplicação DubVideos
* [Front-end Dub Videos](https://github.com/juliano-lopes/dub-videos-front-end)

## Como utilizar
Essa API é responsável por realizar o fluxo de dublagem dos vídeos. Para isso são utilizadas duas outras APIs:  
* API para transcrição e tradução das transcrições:  
[Transcription API](https://github.com/juliano-lopes/transcription-api)  
* E a API para converter o texto da tradução da transcrição em áudio:  
[Text to Speech API](https://github.com/juliano-lopes/text-to-speech-api)  
### Passos para utilizá-la:
* Faça o clone ou baixe o projeto:  
**git clone https://github.com/juliano-lopes/main-dub-videos-api.git**  
* Entre na pasta do projeto:  
**cd main-dub-videos-api**  
* Insira o arquivo com a chave de serviço no caminho:  
**api/config/**
* Será necessário instalar o docker para executar a aplicação em um container.
* Na raiz do projeto, Crie a imagem por meio do Dockerfile:  
**docker build -t dub_videos_main .**  
* Após criar a imagem, certifique-se que uma rede foi criada para que este container e os containers das outras APIs possam se comunicar:
**docker network create dub_videos_network**
* Após criar a rede, suba o container e passe como variáveis os nomes dos hosts para a Transcription API e para Speech Api. Isso quer dizer que você deverá executá-las primeiro, conforme suas instruções, para depois executar essa API principal por meio do comando a seguir:  
**docker run -it --network=dub_videos_network --hostname=dub_videos_main -e T_HOST=dub_videos_transcription -e S_HOST=dub_videos_speech -p 5000:5000 dub_videos_main**  
* A aplicação estará disponível pela porta local 5000
* Abra o endereço:  
http://localhost:5000   
no navegador.  

 ## Como testar

 * para testar a rota de dublagem via upload de arquivo, [baixe este vídeo](https://drive.google.com/file/d/10UoBIsbx1xSGiYY-CP180pMAxoflLJWI/view?usp=sharing) e defina o idioma de origem para pt-BR e o idioma de destino para en-US;
 * para testar a rota via URL, utilize este link 
https://www.youtube.com/shorts/jzQq0QrLJng  
e defina o idioma de origem como en-US e o idioma de destino como pt-BR.
* [Acesse e siga os passos caso deseje utilizar o front-end Dub Videos](https://github.com/juliano-lopes/dub-videos-front-end)

## Apresentação da Aplicação
* [Assista a o vídeo de aprensentação da aplicação Dub Videos](https://youtu.be/ISk4ukqWnfg)