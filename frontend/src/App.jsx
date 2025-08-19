import { useState } from "react";
import {
  Container, TextField, Button, Typography, Card, CardContent, Box
} from "@mui/material";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const generateQueries = async () => {
    setLoading(true);
    setResults([]);

    try {
      const resp = await fetch("http://localhost:8000/llm_keywords", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      const data = await resp.json();
      if (!data.results) throw new Error("No results from backend");

      const torrents = data.results.map((t) => ({
        name: t.name,
        download_status: t.download_status ? "Added to qBittorrent" : "Failed",
        download_error: t.download_error || null,
      }));

      setResults(torrents);
    } catch (err) {
      console.error("Error:", err);
      alert("Something went wrong. See console for details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box className="app-root">
      <Container maxWidth="sm" className="app-container">
        <Typography variant="h3" gutterBottom className="app-title">
          Torrent Downloader
        </Typography>

        <TextField
          fullWidth = "sm"
          label="Enter your request..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="app-input"
          autoComplete="off"
        />

        <Button
          variant="contained"
          onClick={generateQueries}
          disabled={loading || !query}
          className="app-button"
        >
          {loading ? "Processing..." : "Search & Download"}
        </Button>

        {/* Scrollable results */}
        <Box className="results-container">
          {results.map((t, idx) => (
            <Card key={idx} className="result-card">
              <CardContent>
                <Typography variant="body1">{t.name}</Typography>
                <Typography variant="body2" color="textSecondary">
                  Status: {t.download_status}
                </Typography>
                {t.download_error && (
                  <Typography variant="body2" color="error">
                    Error: {t.download_error}
                  </Typography>
                )}
              </CardContent>
            </Card>
          ))}
        </Box>
      </Container>
    </Box>
  );
}

export default App;
