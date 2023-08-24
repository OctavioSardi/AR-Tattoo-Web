import { writeFileSync } from "fs";
import { join, dirname } from "path";
import fetch from "node-fetch";
import { fileURLToPath } from "url"; // To convert import.meta.url to a file path
import potrace from "potrace"; // Import Potrace
import Jimp from "jimp"; // Import Jimp for image manipulation

const YOUR_API_KEY =
  "";

const generateRandomName = () => {
  const randomString = Math.random().toString(36).substring(7);
  return `output_${randomString}`;
};

const generateImage = async () => {
  const formGenerate = new FormData();
  formGenerate.append(
    "prompt",
    "tattoo design, stencil, tattoo stencil, stencil over white background, hyperrealistic, PlayStation 6"
  );

  const generateResponse = await fetch(
    "https://clipdrop-api.co/text-to-image/v1",
    {
      method: "POST",
      headers: {
        "x-api-key": YOUR_API_KEY,
      },
      body: formGenerate,
    }
  );

  const generateBuffer = await generateResponse.arrayBuffer();
  return generateBuffer;
};

const posterizeImage = async (inputPath, outputPath) => {
  const params = {
    threshold: 120, // Adjust threshold as needed
    steps: 4, // Adjust the number of steps
	background: '#fff'
  };

  potrace.posterize(inputPath, params, (err, svg) => {
    if (err) throw err;
    writeFileSync(outputPath, svg);
    console.log(`Vectorized image saved as ${outputPath}`);
  });
};

const runPipeline = async () => {
  try {
    const generatedImageBuffer = await generateImage();

    const outputFileName = generateRandomName();
    const currentFilePath = fileURLToPath(import.meta.url);
    const outputPathPNG = join(dirname(currentFilePath), outputFileName + ".png");
    const outputPathSVG = join(dirname(currentFilePath), outputFileName + ".svg");

    writeFileSync(outputPathPNG, Buffer.from(generatedImageBuffer));

    await posterizeImage(outputPathPNG, outputPathSVG);

    console.log(`Image saved as ${outputFileName}`);
  } catch (error) {
    console.error("Error in pipeline:", error);
  }
};

runPipeline();
