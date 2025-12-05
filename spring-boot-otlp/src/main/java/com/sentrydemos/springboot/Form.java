package com.sentrydemos.springboot;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Form {
	private static final Logger logger = LoggerFactory.getLogger(Application.class);
    private boolean loading;

    public Form() {}

    public Form(boolean loading) {
        this.loading = loading;
    }

    public boolean getLoading() {
        return loading;
    }
    
}